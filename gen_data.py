import time
import random
from typing import List
import string
from transformers import AutoTokenizer
import transformers
import torch
import schema
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f'using device {device} for inference')

model = "meta-llama/Llama-2-7b-chat-hf"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device=device,
)

def gen_random_blog_text():
    prompt = "Please randomly write a blog\n"

    sequences = pipeline(
        prompt,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=100,
    )

    res: str = sequences[0]['generated_text']
    res.replace(prompt, "")

    return res

def gen_comment(blog: str):
    prompt = f'Please write a comment based on the content: \n {blog}'

    sequences = pipeline(
        prompt,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=100,
    )
    res: str = sequences[0]['generated_text']
    res = res.replace(prompt, "")

    return res

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str

if __name__ == "__main__":
    num_users = 20
    num_comments = 100
    num_blogs = 50
    num_likes = 100

    # left for randomly generating likes and comments
    users: List[schema.User]  = []
    blogs: List[schema.Blog] = []
    comments: List[schema.Comment] = []
    likes: List[schema.Like] = []

    user_names = []
    cnt = 0

    engine = create_engine("mysql+pymysql://chan:Diy.2002@localhost/blog", echo=False)
    schema.Base.metadata.create_all(engine)

    with Session(engine) as session:
        while cnt < num_users:
            username = get_random_string(10)
            if username not in user_names:
                user_names.append(username)
                cnt += 1
        
        for uname in user_names:
            user = schema.User(name=uname)
            users.append(user)
        
        session.add_all(users)
        session.commit()

        print('user generated & inserted')

        for i in range(num_blogs):
            user = users[random.randint(0, len(users)-1)]
            content = gen_random_blog_text()

            blog = schema.Blog(content=content, user=user)
            blogs.append(blog)
            print(f'generating [{i+1}/{num_blogs}]')
        
        session.add_all(blogs)
        session.commit()

        print('blog generated & inserted')

        for i in range(num_comments):
            user = users[random.randint(0, len(users)-1)]
            blog = blogs[random.randint(0, len(blogs)-1)]

            content = gen_comment(blog.content)

            comment = schema.Comment(content=content, user=user, blog=blog)
            comments.append(comment)

            print(f'generating [{i+1}/{num_comments}]')
        
        session.add_all(comments)
        session.commit()

        print('comments generated & inserted')

        for i in range(num_likes):
            user = users[random.randint(0, len(users)-1)]
            blog = blogs[random.randint(0, len(blogs)-1)]

            like = schema.Like(like=random.choice([True, False]), user=user, blog=blog)
            likes.append(like)
        
        session.add_all(likes)
        session.commit()

        print('likes generated & inserted')
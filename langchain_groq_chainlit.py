from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl


@cl.on_chat_start
async def on_chat_start():
    
    # Sending an image with the local file path
    elements = [
    cl.Image(name="image1", display="inline", path="groq.jpeg")
    ]
    await cl.Message(content="Hello there, I am Groq. How can I help you ?", elements=elements).send()

    model = ChatGroq(temperature=0,model_name="mixtral-8x7b-32768")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable Machine Learning Engineer.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()

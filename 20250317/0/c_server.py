import asyncio


async def echo(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info("peername"))
    print(me)
    while data := await reader.readline():
        # if data.startswith(b"print"):
        #     writer.write(data[6:])
        # elif data.startswith(b"info"):
        #     writer.write(me.encode())
        writer.write(data)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(echo, "0.0.0.0", 1337)
    async with server:
        await server.serve_forever()


asyncio.run(main())

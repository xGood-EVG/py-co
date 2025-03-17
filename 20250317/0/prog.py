import asyncio
import shlex

async def echo(reader, writer):
    while data := await reader.readline():
        command, *args = shlex.split(data.decode())
        args = str(*args)
        if command == "print":
            writer.write(args.swapcase().encode())
        elif command == "info":
            writer.write(writer.get_extra_info('peername'))
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())

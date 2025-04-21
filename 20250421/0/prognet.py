import asyncio

def sqrootsnet(coeffs: str) -> str:
    try:
        a, b, c = list(map(int, coeffs.split()))
        d = b*b - 4*a*c
        if d < 0:
            return ""
        x1 = (-b + d**0.5) / (2*a)
        x2 = (-b - d**0.5) / (2*a)
        if x1 == x2:
            return f"{x1}"
        return f"{x1} {x2}"
    except:
        return ""

async def echo(reader, writer):
    while data := await reader.read():
        print(data)
        result = sqrootsnet(data)
        writer.write(result)
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

def serve():
    asyncio.run(main())


import asyncio

def sqroots(coeffs: str) -> str:
    a, b, c = list(map(int, coeffs.split()))
    d = b*b - 4*a*c
    if d < 0:
        return ""
    x1 = (-b + d**0.5) / (2*a)
    x2 = (-b - d**0.5) / (2*a)
    if x1 == x2:
        return f"{x1}"
    return f"{x1} {x2}"

async def echo(reader, writer):
    while data := await reader.readline():
        writer.write(data.swapcase())
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())


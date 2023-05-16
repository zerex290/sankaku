---
title: About HttpClient
---

There is nothing special to say about HttpClient: its mere class with
`aiohttp.ClientSession` instance inside, custom response type (with already
awaited json response) and header forwarding to each request to server.

If logging is enabled, each request and response will be displayed in terminal.
# Introduction

There are several clients present and each of them is has different responsibilities,
but for simplicity they all are merged into one client with multiple inheritance -
`SankakuClient()`. If you want to use any specific client, then you should
import it explicitly: `from sankaku.clients import <client>`.
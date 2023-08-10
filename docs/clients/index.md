# Introduction

There are several clients present and each of them has different responsibilities,
but for simplicity they all are merged into one client with multiple inheritance -
`SankakuClient()`. If you want to use any specific client, then you should
import it explicitly: `from sankaku.clients import <client>`.

## Specifying the range

It's worth mentioning that any client methods with return type `AsyncIterator`
supports specyfing of range (except `PostClient.get_post_comments()`) in the 
same way as with using python built-in `range(_start, _stop, _step)` function.

The only restrictions when setting range:

- Initial value can't be 0;
- Can't use negative `_step`;
- `_start` value should always be less than `_end`.

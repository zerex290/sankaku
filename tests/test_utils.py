from datetime import datetime

import pytest

from sankaku import utils, errors


@pytest.mark.parametrize(
    ["rps", "rpm", "expected"],
    [(200, 200, errors.RateLimitError), (None, None, TypeError)]
)
async def test_ratelimit_with_incompatible_args(rps, rpm, expected):  # noqa: D103
    with pytest.raises(expected):
        @utils.ratelimit(rps=rps, rpm=rpm)
        async def idle_request():
            assert True

        await idle_request()


@pytest.mark.parametrize(["rps", "rpm"], [(3, None), (180, None)])
async def test_ratelimit(rps, rpm):  # noqa: D103
    @utils.ratelimit(rps=rps, rpm=rpm)
    async def idle_request():
        assert True

    await idle_request()


@pytest.mark.parametrize(
    ["ts", "expected"],
    [
        (
            {
                "json_class": "Time",
                "s": 1680471860,
                "n": 0
            },
            datetime.utcfromtimestamp(1680471860).astimezone()
        ),
        (
            {
                "json_class": "Time",
                "s": None,
                "n": 0
            },
            None
        ),
    ]
)
def test_convert_ts_to_datetime(ts, expected):  # noqa: D103
    assert utils.convert_ts_to_datetime(ts) == expected

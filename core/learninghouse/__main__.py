import sys

from pydantic import ValidationError

DOCUMENTATION_URL = (
    "https://learninghouseservice.github.io/learninghouse/configuration/"
)


def report_invalid_configuration(error: ValidationError) -> int:
    print(
        "learningHouse cannot start: the configuration is not valid.\n",
        file=sys.stderr,
    )

    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"]) or "configuration"
        message = str(detail["msg"]).removeprefix("Value error, ")
        print(f"  {location}: {message}", file=sys.stderr)

    print(f"\nSee {DOCUMENTATION_URL}", file=sys.stderr)

    return 1


def main() -> int:
    try:
        from learninghouse.service import run
    except ValidationError as error:
        return report_invalid_configuration(error)

    run()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

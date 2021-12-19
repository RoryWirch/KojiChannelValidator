import argparse
import koji_channel_validator.koji_channel_validator as cv


def main():
    """
    Collect any command line arguments for the tool and launch the tool.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--log", action="store_true", help="Produces logging info for the tool"
    )
    parser.add_argument(
        "-c", "--channel", required=True, help="Sets the channel name being validated"
    )
    args = parser.parse_args()

    exit(cv.check(args))


if __name__ == "__main__":
    main()

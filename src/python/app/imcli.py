"""Main module for imcli program entrypoint"""

from app.command.parser import get_parser


def main() -> None:
    """Main entrypoint for imcli program"""
    args = get_parser().parse_args()
    return args.func(args)


if __name__ == '__main__':
    main()

from app.command.parser import get_parser


def main() -> None:
    args = get_parser().parse_args()
    return args.func(args)

if __name__ == '__main__':
    main()

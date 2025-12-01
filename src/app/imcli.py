from app.cmd.parser import get_parser


def main() -> None:
    args = get_parser().parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
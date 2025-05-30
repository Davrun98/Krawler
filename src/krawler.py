import argparse

from orchestrator.orchestrator import Orchestrator


def parse_args():
    parser = argparse.ArgumentParser(description="Krawler - a kroutine web utility")

    parser.add_argument(
        '-s', '--subdomain',
        default='www',
        help="Subdomain to crawl (default: www)"
    )

    parser.add_argument(
        '-H', '--host',
        required=True,
        help="Root domain to crawl (e.g. example-domain.com)"
    )

    parser.add_argument(
        '-p', '--path',
        default='/',
        help="Path to crawl on the host (default: /)"
    )

    parser.add_argument(
        '-l', '--recursion-limit',
        type=int,
        default=5,
        help="Maximum recursion depth (default: 5; use -1 for unlimited - this might make bad things happen)"
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    orchestrator = Orchestrator(args.subdomain, args.host, args.recursion_limit)

    base_link = f"{args.subdomain}.{args.host}{args.path}"
    orchestrator.run(base_link)

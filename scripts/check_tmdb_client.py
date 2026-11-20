from source_system.tmdb_client import TMDbClient


def main():
    client = TMDbClient(force_refresh=True)

    movie = client.fetch(155, "movie")
    credits = client.fetch(155, "credits")

    assert movie is not None
    assert movie["id"] == 155
    assert "title" in movie
    assert credits is not None
    assert "cast" in credits

    print("Movie:", movie["title"])
    print("Cast entries:", len(credits["cast"]))
    print("Client checks passed.")


if __name__ == "__main__":
    main()

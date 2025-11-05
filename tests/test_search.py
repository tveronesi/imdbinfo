from imdbinfo import search_title

def test_basic_search():
    search_title("Matrix")

if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)s - %(levelname)s - %(message)s"
    )
    
    test_basic_search()

import unittest
import tempfile
import os
import zipfile, json, gzip
from wacz.main import main, now
from unittest.mock import patch
import jsonlines

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


class TestWaczFormat(unittest.TestCase):
    @patch("wacz.main.now")
    def test_warc_with_detect_pages_flag(self, mock_now):
        """When passing the text index flag pages/pages.jsonl should be generated."""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-url.wacz"),
                        "--detect-pages",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-url.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_pages"))
                zip_ref.close()

            wacz_pages = os.path.join(tmpdir, "unzipped_valid_pages/pages/pages.jsonl")
            wacz_cdx = os.path.join(tmpdir, "unzipped_valid_pages/indexes/index.cdx.gz")
            cdx_content = gzip.open(wacz_cdx, "rb").read()
            self.assertTrue(
                "pages.jsonl"
                in os.listdir(os.path.join(tmpdir, "unzipped_valid_pages/pages/"))
            )
            with open(wacz_pages) as f:
                for _ in range(1):
                    next(f)
                for line in f:
                    obj = json.loads(line)
                    self.assertTrue("id" in obj.keys())
                    self.assertTrue("ts" in obj.keys())
                    self.assertTrue("title" in obj.keys())
                    self.assertTrue("url" in obj.keys())
                    self.assertTrue(obj["url"].encode() in cdx_content)

    @patch("wacz.main.now")
    def test_warc_with_text_index_flag(self, mock_now):
        """When passing the text index flag pages/pages.jsonl should be generated with a full and accurate text index."""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-url.wacz"),
                        "-t",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-url.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_text"))
                zip_ref.close()

            wacz_pages = os.path.join(tmpdir, "unzipped_valid_text/pages/pages.jsonl")
            wacz_cdx = os.path.join(tmpdir, "unzipped_valid_text/indexes/index.cdx.gz")
            cdx_content = gzip.open(wacz_cdx, "rb").read()
            self.assertTrue(
                "pages.jsonl"
                in os.listdir(os.path.join(tmpdir, "unzipped_valid_text/pages/"))
            )
            with open(wacz_pages) as f:
                for _ in range(1):
                    next(f)
                for line in f:
                    obj = json.loads(line)
                    self.assertTrue("id" in obj.keys())
                    self.assertTrue("ts" in obj.keys())
                    self.assertTrue("title" in obj.keys())
                    self.assertTrue("url" in obj.keys())
                    self.assertTrue(obj["url"].encode() in cdx_content)
                    self.assertTrue("text" in obj.keys())

    def test_warc_with_only_ts_flag(self):
        """If a user only passes the --ts flag we should return an error and a message about needing to also pass the --url flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(SystemExit):
                self.assertTrue(
                    main(
                        [
                            "create",
                            "-f",
                            os.path.join(TEST_DIR, "example-collection.warc"),
                            "-o",
                            os.path.join(tmpdir, "example-collection.wacz"),
                            "--ts",
                            "2020104212236",
                        ]
                    )
                )

    @patch("wacz.main.now")
    def test_warc_with_valid_date_flag(self, mock_now):
        """When passing a valid date flag the datapackage should have that as the mainpageTS"""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-desc.wacz"),
                        "--desc",
                        "fake desc",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-desc.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_desc"))
                zip_ref.close()

            self.wacz_json = os.path.join(
                tmpdir, "unzipped_valid_desc/datapackage.json"
            )
            self.wacz_pages = os.path.join(
                tmpdir, "unzipped_valid_desc/pages/pages.jsonl"
            )

            f = open(self.wacz_json, "rb")
            json_parse = json.loads(f.read())

            self.assertEqual(json_parse["des"], "fake desc")

    @patch("wacz.main.now")
    def test_warc_with_valid_date_flag(self, mock_now):
        """When passing a valid title flag the datapackage should have that as the title value"""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-title.wacz"),
                        "--title",
                        "Example Title",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-title.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_title"))
                zip_ref.close()

            self.wacz_json = os.path.join(
                tmpdir, "unzipped_valid_title/datapackage.json"
            )
            self.wacz_pages = os.path.join(
                tmpdir, "unzipped_valid_title/pages/pages.jsonl"
            )

            f = open(self.wacz_json, "rb")
            json_parse = json.loads(f.read())

            self.assertEqual(json_parse["title"], "Example Title")

    @patch("wacz.main.now")
    def test_warc_with_valid_date_flag(self, mock_now):
        """When passing a valid date flag the datapackage should have that as the mainpageTS"""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-date.wacz"),
                        "--date",
                        "2020-11-01",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-date.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_date"))
                zip_ref.close()

            self.wacz_json = os.path.join(
                tmpdir, "unzipped_valid_date/datapackage.json"
            )
            self.wacz_pages = os.path.join(
                tmpdir, "unzipped_valid_date/pages/pages.jsonl"
            )

            f = open(self.wacz_json, "rb")
            json_parse = json.loads(f.read())

            self.assertEqual(json_parse["metadata"]["mainPageTS"], "2020-11-01")

    @patch("wacz.main.now")
    def test_warc_with_valid_url_flag(self, mock_now):
        """When passing a valid url flag the url should be added to the pages.jsonl file and appear in the datapackage"""
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection-valid-url.wacz"),
                        "--url",
                        "http://www.example.com/",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-url.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_url"))
                zip_ref.close()

            self.wacz_json = os.path.join(tmpdir, "unzipped_valid_url/datapackage.json")
            self.wacz_pages = os.path.join(
                tmpdir, "unzipped_valid_url/pages/pages.jsonl"
            )

            f = open(self.wacz_json, "rb")
            json_parse = json.loads(f.read())

            f = open(self.wacz_pages, "rb")
            json_pages = [json.loads(jline) for jline in f.read().splitlines()]
            self.assertEqual(json_pages[1]["url"], "http://www.example.com/")
            self.assertEqual(
                json_parse["metadata"]["mainPageURL"], "http://www.example.com/"
            )
            assert "mainPageTS" not in json_parse.keys()

    def test_warc_with_invalid_url_flag(self):
        """When passing an invalid url flag we should raise a ValueError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection.wacz"),
                        "--url",
                        "http://www.examplefake.com/",
                    ]
                )

    def test_warc_with_valid_url_and_invalid_ts_flag(self):
        """When passing a valid url flag with an invalid ts flag we should raise a ValueError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(tmpdir, "example-collection.wacz"),
                        "--url",
                        "http://www.example.com/",
                        "--ts",
                        "2020104212236",
                    ]
                )

    @patch("wacz.main.now")
    def test_warc_with_valid_url_and_ts_flag(self, mock_now):
        mock_now.return_value = (2020, 10, 7, 22, 29, 10)
        """When passing an a valid url and ts flag we should see those values represented in the datapackage and pages.jsonl file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(
                main(
                    [
                        "create",
                        "-f",
                        os.path.join(TEST_DIR, "example-collection.warc"),
                        "-o",
                        os.path.join(
                            tmpdir, "example-collection-valid-url-valid-ts.wacz"
                        ),
                        "--url",
                        "http://www.example.com/",
                        "--ts",
                        "20201007212236",
                    ]
                )
            )
            with zipfile.ZipFile(
                os.path.join(tmpdir, "example-collection-valid-url-valid-ts.wacz"), "r"
            ) as zip_ref:
                zip_ref.extractall(os.path.join(tmpdir, "unzipped_valid_url_valid_ts"))
                zip_ref.close()

            self.wacz_json = os.path.join(
                tmpdir, "unzipped_valid_url_valid_ts/datapackage.json"
            )
            self.wacz_pages = os.path.join(
                tmpdir, "unzipped_valid_url_valid_ts/pages/pages.jsonl"
            )

            f = open(self.wacz_json, "rb")
            json_parse = json.loads(f.read())

            f = open(self.wacz_pages, "rb")
            json_pages = [json.loads(jline) for jline in f.read().splitlines()]
            self.assertEqual(json_pages[1]["url"], "http://www.example.com/")
            self.assertEqual(
                json_parse["metadata"]["mainPageURL"], "http://www.example.com/"
            )
            self.assertEqual(json_parse["metadata"]["mainPageTS"], "20201007212236")


if __name__ == "__main__":
    unittest.main()

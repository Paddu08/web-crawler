import unittest
from crawl import normalize_url,get_h1_from_html,get_first_paragraph_from_html,get_urls_from_html,get_images_from_html,extract_page_data,get_html,crawl


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    def test_get_h1_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
        <p>Outside paragraph.</p>
        <main>
            <p>Main paragraph.</p>
        </main>
    </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)


    def test_get_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_normalize_url_trailing_slash(self):
        input_url = "https://blog.boot.dev/path/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path/"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_missing(self):
        input_body = '<html><body></body></html>'
        actual = get_h1_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_outside_main(self):
        input_body = '<html><body><p>Only paragraph.</p></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = "Only paragraph."
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://blog.boot.dev/articles/"
        input_body = '<html><body><a href="/about">About</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/about"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="https://blog.boot.dev/logo.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_normalize_url_root(self):
        input_url = "https://blog.boot.dev"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1"],
            "image_urls": ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_get_urls_with_fragment(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="/page#section">Page</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/page#section"]
        self.assertEqual(actual, expected)

    def test_get_images_no_src(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img alt="No src"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_no_images(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><h1>Only</h1><p>Para</p></body></html>'
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Only",
            "first_paragraph": "Para",
            "outgoing_links": [],
            "image_urls": []
        }
        self.assertEqual(actual, expected)

    def test_normalize_url_with_port(self):
        input_url = "http://example.com:80/path"
        actual = normalize_url(input_url)
        expected = "example.com:80/path"
        self.assertEqual(actual, expected)

    def test_get_urls_with_parent_relative(self):
        input_url = "https://blog.boot.dev/articles/"
        input_body = '<html><body><a href="../about">About</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/about"]
        self.assertEqual(actual, expected)

    def test_get_html_success(self):
        from unittest.mock import patch, Mock
        with patch('crawl.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.text = '<html><body>ok</body></html>'
            mock_get.return_value = mock_resp
            actual = get_html('https://example.com')
            self.assertEqual(actual, '<html><body>ok</body></html>')
            mock_get.assert_called_once_with('https://example.com', headers={"User-Agent": "BootCrawler/1.0"}, timeout=10)

    def test_get_html_raises_on_error(self):
        from unittest.mock import patch, Mock
        import requests
        with patch('crawl.requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.raise_for_status.side_effect = requests.HTTPError('404')
            mock_get.return_value = mock_resp
            with self.assertRaises(requests.HTTPError):
                get_html('https://example.com')

    def test_crawl_basic_same_domain(self):
        from unittest.mock import patch

        base = 'https://blog.boot.dev'
        page1 = '<html><body><h1>Page1</h1><a href="/page2">Next</a></body></html>'
        page2 = '<html><body><h1>Page2</h1></body></html>'

        def fake_get_html(url):
            if url == base:
                return page1
            if url == base + '/page2':
                return page2
            return ''

        with patch('crawl.get_html', side_effect=fake_get_html):
            data = {}
            crawl(base, base, data)
            self.assertIn('blog.boot.dev', data)
            self.assertIn('blog.boot.dev/page2', data)
            self.assertEqual(data['blog.boot.dev']['h1'], 'Page1')
            self.assertEqual(data['blog.boot.dev/page2']['h1'], 'Page2')

    def test_crawl_skips_other_domain(self):
        from unittest.mock import patch

        base = 'https://blog.boot.dev'
        page = '<html><body><h1>Home</h1><a href="https://other.com/page">Other</a></body></html>'

        with patch('crawl.get_html', return_value=page):
            data = {}
            crawl(base, base, data)
            # only blog.boot.dev should be present
            self.assertIn('blog.boot.dev', data)
            self.assertNotIn('other.com/page', data)

    def test_crawl_avoids_revisit(self):
        from unittest.mock import patch

        base = 'https://blog.boot.dev'
        page1 = '<html><body><h1>Page1</h1><a href="/page2">Next</a></body></html>'
        page2 = '<html><body><h1>Page2</h1><a href="/">Back</a></body></html>'

        def fake_get_html(url):
            if url == base:
                return page1
            if url == base + '/page2':
                return page2
            return ''

        with patch('crawl.get_html', side_effect=fake_get_html):
            data = {}
            crawl(base, base, data)
            # ensure both pages crawled and no infinite loop
            self.assertEqual(set(data.keys()), {'blog.boot.dev', 'blog.boot.dev/page2'})


if __name__ == "__main__":
    unittest.main()


    
import webbrowser


class WebBrowserLauncher:
    def open(self, url: str) -> None:
        if not webbrowser.open(url):
            raise RuntimeError(
                "Could not open authorization URL in a browser."
            )

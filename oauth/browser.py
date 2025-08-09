import webbrowser


class WebBrowserLauncher:
    def open(self, url: str) -> None:
        webbrowser.open(url)

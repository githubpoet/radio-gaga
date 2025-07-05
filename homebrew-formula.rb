class RadioGaga < Formula
  include Language::Python::Virtualenv

  desc "Radio Gaga - Terminal User Interface for Radio Streaming"
  homepage "https://github.com/githubpoet/radio-gaga"
  url "https://github.com/githubpoet/radio-gaga/archive/v1.0.0.tar.gz"
  sha256 "7eb6207e6130aa7c39b3ea9618f5ee78163958bdbbb08c52460e7bbf42f025db"
  license "MIT"

  depends_on "python@3.11"
  depends_on "ffmpeg"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/9d/be/10918a2eac4ae9f02f6cfe6414b7a155ccd8f7f9d4380d62fd5b955065c5e/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/cd/e5/af35f7ea75cf72f2cd079c95ee16797de7cd71f29ea7c68ae5ce7be1eda94/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test that the command exists and shows help
    system "#{bin}/radio-gaga", "--help"
  end
end

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://sillok-english.deif79.chatgpt.site"),
  title: { default: "Open Sillok — The Joseon Annals in English", template: "%s | Open Sillok" },
  description: "Read new English translations of selected Joseon annals alongside the Classical Chinese originals, with article-level sources and transparent review status.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Market Terminal",
  description: "Real-time market simulation dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* suppressHydrationWarning per Context7 React hydration docs: /websites/react_dev_reference */}
      <body className="antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}

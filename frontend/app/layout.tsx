import type { ReactNode } from "react";
import "./globals.css";
import "./brand.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}

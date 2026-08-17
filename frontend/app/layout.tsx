import type { ReactNode } from "react";
import "./globals.css";
import "./auth.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}

import type { ReactNode } from "react";
import "./globals.css";
<<<<<<< HEAD
import "./auth.css";
=======
import "./brand.css";
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}

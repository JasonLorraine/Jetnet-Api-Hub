export const metadata = {
  title: "JETNET Aircraft Lookup",
  description: "Look up aircraft by tail number using the JETNET API",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

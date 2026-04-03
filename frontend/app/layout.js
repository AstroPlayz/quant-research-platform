import './globals.css'

export const metadata = {
  title: 'Quant Research Platform',
  description: 'Production-grade quant research dashboard',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

import Dashboard from "../components/Dashboard";

/**
 * Simple App Router page that delegates to the Dashboard client component.
 */
export default function Home() {
  // App Router page component per Context7 Next.js docs: /vercel/next.js installation + App Router page structure.
  return <Dashboard />;
}

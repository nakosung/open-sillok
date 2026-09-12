import Link from "next/link";
import {SiteHeader} from "@/components/site-header";
export default function NotFound(){return <><SiteHeader/><main className="not-found"><p className="eyebrow">ENTRY NOT FOUND</p><h1>This page is not in the current edition.</h1><p>The article may not yet have an English translation here. Browse the available entries or follow the original archive.</p><Link href="/">Return to the reading room</Link></main></>;}

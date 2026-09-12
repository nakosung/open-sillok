import Link from "next/link";
import {ArrowUpRight} from "lucide-react";
export function SiteHeader({current="read"}:{current?:"read"|"about"|"contribute"}){
  return <header className="masthead"><Link href="/" className="brand" aria-label="Open Sillok reading room"><span className="seal" lang="zh-Hant">實</span><span className="brand-name">Open Sillok<span className="brand-caption">THE JOSEON ANNALS</span></span></Link><nav aria-label="Main navigation"><Link href="/" aria-current={current==="read"?"page":undefined}>Reading room</Link><Link href="/about" aria-current={current==="about"?"page":undefined}>Edition & sources</Link><Link href="/contribute" aria-current={current==="contribute"?"page":undefined}>Contribute</Link><a href="https://sillok.history.go.kr/" target="_blank" rel="noreferrer" className="archive-link">Original archive <ArrowUpRight size={15}/></a></nav></header>;
}

"use client";
import {useState} from "react";
import Link from "next/link";
import {ArrowUpRight, BookOpen, Copy, Check} from "lucide-react";
import {editUrl,historyUrl,issueUrl} from "@/lib/project";
import {Tabs, TabsList, TabsTrigger, TabsContent} from "@/components/ui/tabs";
import {entryDate, sourceUrl, citation, reviewLabel, type Entry} from "@/lib/entry";

export function EntryReader({entry, standalone = false}: {entry: Entry; standalone?: boolean}) {
  const [copied,setCopied] = useState(false);
  const [copyError,setCopyError] = useState(false);
  const [view,setView] = useState("parallel");
  const copy = async () => {try {await navigator.clipboard.writeText(citation(entry));setCopied(true);setCopyError(false);setTimeout(()=>setCopied(false),2200);} catch {setCopyError(true);}};
  const english = <section className="english-text"><p className="column-label">ENGLISH TRANSLATION</p>{entry.translation.map((p,i)=><p key={i}>{p}</p>)}</section>;
  const original = <section className="original-text" lang="lzh"><p className="column-label" lang="en">CLASSICAL CHINESE · 原文</p>{entry.original.split("\n").map((p,i)=><p key={i}>{p}</p>)}</section>;
  return <article className={`reader ${standalone?"standalone-reader":""}`} aria-labelledby="entry-title">
    <div className="reader-topline"><span className="eyebrow">{entry.king}<span className="separator">/</span>{entry.year}</span><span className="draft-label">{reviewLabel(entry)}</span></div>
    <h1 id="entry-title" tabIndex={-1}>{entry.title}</h1><p className="entry-dateline">{entryDate(entry)} <span>·</span> Volume {entry.volume}, entry {entry.ordinal}</p>
    <p className="calendar-note">Original lunisolar date.{entry.dayName?` Sexagenary day: ${entry.dayName}.`:""}{entry.dateScope==="month"?" Monthly entry; no exact event day is stated.":""}</p><div className="topic-row">{entry.topics.map(t=><span key={t}>{t}</span>)}</div>
    <Tabs value={view} onValueChange={setView} className="reading-tabs"><div className="reader-toolbar"><TabsList variant="line" className="view-tabs"><TabsTrigger value="parallel">Parallel text</TabsTrigger><TabsTrigger value="english">English</TabsTrigger><TabsTrigger value="original">Original</TabsTrigger></TabsList><button onClick={copy} className="icon-action" aria-label={copied?"Citation copied":"Copy citation"} title="Copy citation">{copied?<Check size={17}/>:<Copy size={17}/>}<span>{copied?"Copied":"Cite"}</span></button></div><TabsContent value="parallel"><div className="parallel-columns">{english}{original}</div></TabsContent><TabsContent value="english"><div className="single-text">{english}</div></TabsContent><TabsContent value="original"><div className="single-text">{original}</div></TabsContent></Tabs>
    <span className="sr-only" role="status">{copied?"Citation copied to clipboard":""}</span>{copyError&&<p className="copy-feedback" role="status">Copy is unavailable in this browser. Select the citation below.</p>}
    {entry.notes.length>0&&<section className="reading-notes"><h2><BookOpen size={17}/>Reading notes</h2>{entry.notes.map((n,i)=><div className="reading-note" key={n.title}><span className="note-number">{String(i+1).padStart(2,"0")}</span><div><h3>{n.title}</h3><p>{n.text}</p></div></div>)}</section>}
    <footer className="entry-source"><p className="column-label">SOURCE & TRANSLATION</p><a href={sourceUrl(entry)} target="_blank" rel="noreferrer">View this entry at the National Institute of Korean History <ArrowUpRight size={15}/></a><p className="source-description">A new English translation of the Classical Chinese text. This edition is independent of the official archive. Review status applies to the exact text shown here.</p><p className="source-description">{entry.provenance.method} · Contributors: {entry.provenance.contributors.join(", ")} · Model: {entry.provenance.model}. <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a></p>{entry.reviews.map(r=><p className="source-description" key={r.reviewer+r.date}><a href={r.evidenceUrl} target="_blank" rel="noreferrer">{r.level} review by {r.reviewer}</a> · {r.scope} · {r.date}</p>)}<div className="contribution-links">{editUrl(entry.id)?<><a href={editUrl(entry.id)!} target="_blank" rel="noreferrer">Suggest an edit</a><a href={historyUrl(entry.id)!} target="_blank" rel="noreferrer">Revision history</a><a href={issueUrl(entry.id)!} target="_blank" rel="noreferrer">Report a correction</a></>:<Link href={`/contribute?entry=${entry.id}`}>Help improve this translation <ArrowUpRight size={14}/></Link>}</div><details open={copyError}><summary>Full citation & version</summary><p className="full-citation">{citation(entry)}</p></details>{!standalone&&<Link className="permalink" href={`/entry/${entry.id}`}>Open permanent entry page <ArrowUpRight size={15}/></Link>}</footer>
  </article>;
}

"use client";
import {useEffect,useRef,useState} from "react";
import Link from "next/link";
import {Search,ArrowUpRight,ChevronRight,ChevronLeft,BookOpen,X,ArrowDown} from "lucide-react";
import {Select,SelectTrigger,SelectContent,SelectItem,SelectValue} from "@/components/ui/select";
import {SiteHeader} from "./site-header";
import {EntryReader} from "./entry-reader";
import {edition,type Entry,type SearchResult} from "@/lib/entry";

type Filters={q:string;king:string;topic:string;open:boolean};
type Props={initialResult:SearchResult;initialEntry:Entry|null;initialFilters:Filters;options:{kings:string[];topics:string[]};editionCount:number};
export function ReadingRoom({initialResult,initialEntry,initialFilters,options,editionCount}:Props) {
  const [query,setQuery]=useState(initialFilters.q),[king,setKing]=useState(initialFilters.king),[topic,setTopic]=useState(initialFilters.topic);
  const [result,setResult]=useState(initialResult),[selectedId,setSelectedId]=useState(initialEntry?.id??null),[selected,setSelected]=useState(initialEntry);
  const [mobileReader,setMobileReader]=useState(initialFilters.open),[searching,setSearching]=useState(false),[moreLoading,setMoreLoading]=useState(false);
  const [searchError,setSearchError]=useState(""),[entryError,setEntryError]=useState(""),[retry,setRetry]=useState(0);
  const first=useRef(true),restored=useRef<string|null>(null),activeFilter=useRef("");
  const filterKey=new URLSearchParams({q:query,king,topic}).toString();activeFilter.current=filterKey;
  useEffect(()=>{
    if(first.current){first.current=false;return;}
    const controller=new AbortController();setSearching(true);setSearchError("");setMoreLoading(false);
    const timer=setTimeout(async()=>{
      try{
        const response=await fetch(`/api/entries?${filterKey}`,{signal:controller.signal});if(!response.ok)throw new Error("Search unavailable");
        const data:SearchResult=await response.json();if(controller.signal.aborted)return;
        setResult(data);setSelectedId(restored.current??data.items[0]?.id??null);restored.current=null;setSearching(false);
      }catch(error){if(!controller.signal.aborted){setSearchError(error instanceof Error?error.message:"Search unavailable");setSearching(false);}}
    },180);
    return()=>{clearTimeout(timer);controller.abort();};
  },[filterKey,retry]);
  useEffect(()=>{
    if(!selectedId){setSelected(null);return;}
    const controller=new AbortController();setEntryError("");
    if(selectedId===initialEntry?.id){setSelected(initialEntry);return;}
    setSelected(null);
    fetch(`/api/entries/${encodeURIComponent(selectedId)}`,{signal:controller.signal}).then(async response=>{
      if(!response.ok)throw new Error("This entry could not be loaded.");const entry:Entry=await response.json();if(!controller.signal.aborted)setSelected(entry);
    }).catch(error=>{if(!controller.signal.aborted)setEntryError(error instanceof Error?error.message:"This entry could not be loaded.");});
    return()=>controller.abort();
  },[selectedId,initialEntry,retry]);
  useEffect(()=>{
    const restore=()=>{const p=new URLSearchParams(window.location.search);const id=p.get("entry");restored.current=id;setQuery((p.get("q")??"").slice(0,300));setKing(options.kings.includes(p.get("king")??"")?p.get("king")!:"all");setTopic(options.topics.includes(p.get("topic")??"")?p.get("topic")!:"all");setSelectedId(id);setMobileReader(!!id);setRetry(n=>n+1);};
    window.addEventListener("popstate",restore);return()=>window.removeEventListener("popstate",restore);
  },[options]);
  useEffect(()=>{
    const p=new URLSearchParams();if(query)p.set("q",query);if(king!=="all")p.set("king",king);if(topic!=="all")p.set("topic",topic);if(mobileReader&&selectedId)p.set("entry",selectedId);
    window.history.replaceState(window.history.state,"",p.size?`/?${p}`:"/");
  },[query,king,topic,mobileReader,selectedId]);
  useEffect(()=>{
    if(mobileReader&&selected&&window.matchMedia("(max-width:700px)").matches){document.getElementById("entry-title")?.focus({preventScroll:true});window.scrollTo({top:0,behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});}
  },[mobileReader,selected]);
  const choose=(id:string)=>{setSelectedId(id);setMobileReader(true);};
  const reset=()=>{setQuery("");setKing("all");setTopic("all");setMobileReader(false);};
  const backToList=()=>{setMobileReader(false);requestAnimationFrame(()=>document.querySelector<HTMLButtonElement>(".entry-card.selected")?.focus());};
  const loadMore=async(chooseNext=false)=>{
    if(result.nextOffset===null||moreLoading||searching)return;const key=filterKey;setMoreLoading(true);setSearchError("");
    try{const response=await fetch(`/api/entries?${key}&offset=${result.nextOffset}`);if(!response.ok)throw new Error("More entries could not be loaded.");const data:SearchResult=await response.json();if(activeFilter.current!==key)return;setResult(old=>({...data,offset:0,items:[...old.items,...data.items]}));if(chooseNext&&data.items[0])choose(data.items[0].id);}
    catch(error){if(activeFilter.current===key)setSearchError(error instanceof Error?error.message:"More entries could not be loaded.");}
    finally{if(activeFilter.current===key)setMoreLoading(false);}
  };
  const index=result.items.findIndex(e=>e.id===selectedId);
  const next=()=>{if(index>=0&&index+1<result.items.length)choose(result.items[index+1].id);else void loadMore(true);};
  return <><a href="#reading-room" className="skip-link">Skip to reading room</a><SiteHeader/><section className="room-intro"><div><p className="eyebrow">AN ENGLISH EDITION, BUILT TOGETHER</p><h1>The Joseon Annals</h1><p>Read the record. Follow the source. <Link href="/contribute">Help translate it.</Link></p></div><div className="edition-meta"><span className="edition-numeral">{editionCount}</span><span>entries in this edition<Link href="/about">Scope & review status <ArrowUpRight size={13}/></Link></span></div></section>
    <main id="reading-room" className={`reading-room ${mobileReader&&selectedId?"show-reader":""}`}><aside className="catalog" aria-label="Search and browse entries"><div className="catalog-tools"><label htmlFor="search" className="column-label">FIND AN ENTRY</label><div className="search-box"><Search size={18}/><input id="search" type="search" maxLength={300} placeholder="Search English, 한국어, 漢文…" value={query} onChange={e=>setQuery(e.target.value)}/>{query&&<button aria-label="Clear search" onClick={()=>setQuery("")}><X size={16}/></button>}</div><div className="filter-row"><Select value={king} onValueChange={setKing}><SelectTrigger aria-label="Filter by reign"><SelectValue/></SelectTrigger><SelectContent><SelectItem value="all">All reigns</SelectItem>{options.kings.map(k=><SelectItem key={k} value={k}>{k}</SelectItem>)}</SelectContent></Select><Select value={topic} onValueChange={setTopic}><SelectTrigger aria-label="Filter by topic"><SelectValue/></SelectTrigger><SelectContent><SelectItem value="all">All topics</SelectItem>{options.topics.map(t=><SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent></Select></div><div className="results-meta" aria-live="polite"><span>{searching?"Searching…":`${result.total} ${result.total===1?"entry":"entries"}`}</span>{query||king!=="all"||topic!=="all"?<button onClick={reset}>Reset filters</button>:<span>Selected records</span>}</div>{searchError&&<p className="request-error" role="alert">{searchError} <button onClick={()=>setRetry(n=>n+1)}>Retry search</button></p>}</div>
    <div className="catalog-results" aria-busy={searching}>{result.items.map(e=><button key={e.id} disabled={searching} className={`entry-card ${selectedId===e.id?"selected":""}`} onClick={()=>choose(e.id)} aria-pressed={selectedId===e.id}><span className="entry-card-meta">{e.king}<span>{e.year}</span></span><span className="entry-card-title">{e.title}</span><span className="entry-card-bottom"><span>{e.leapMonth?"Intercalary month":"Month"} {e.month}{e.dateScope!=="month"?` · Day ${e.day}`:" · Monthly entry"}</span><ChevronRight size={16}/></span></button>)}{result.total===0&&!searching&&<div className="empty-results"><Search size={26}/><h2>No matching entries</h2><p>Try a person, topic, year, or a shorter phrase. Search covers only this edition.</p><button onClick={reset}>Show all entries</button></div>}{result.nextOffset!==null&&<button className="more-results" disabled={moreLoading||searching} onClick={()=>void loadMore()}>{moreLoading?"Loading…":"Show more entries"}<ArrowDown size={16}/></button>}</div><div className="catalog-foot"><span lang="zh-Hant">朝鮮王朝實錄</span><p>Original texts preserved.<br/>Every contribution traceable.</p></div></aside>
    <div className="reader-panel"><div className="reader-navigation"><button className="back-to-list" onClick={backToList}><ChevronLeft size={16}/>All entries</button><span className="reader-position">READING ROOM <span>/</span> {index<0?"SELECTED ENTRY":`${String(index+1).padStart(2,"0")} OF ${result.total}`}</span><div><button aria-label="Previous entry" disabled={index<=0||searching} onClick={()=>choose(result.items[index-1].id)}><ChevronLeft size={18}/></button><button aria-label="Next entry" disabled={index<0||searching||moreLoading||(index===result.items.length-1&&result.nextOffset===null)} onClick={next}><ChevronRight size={18}/></button></div></div>{selected?<EntryReader key={selected.id} entry={selected}/>:<div className="reader-empty" role="status"><BookOpen size={36}/><h2>{entryError?"Entry unavailable":selectedId?"Loading entry…":"Your reading room"}</h2><p>{entryError||(!selectedId?"Adjust the search or filters to find an entry.":"")}</p>{entryError&&<button className="text-link" onClick={()=>setRetry(n=>n+1)}>Try again</button>}</div>}</div></main>
    <footer className="site-footer"><p>Open Sillok<span>Independent community edition · {edition.date}</span></p><Link href="/contribute">Bring your AI. Contribute one entry. <ArrowUpRight size={14}/></Link></footer></>;
}

import project from "@/project.json";

export type Review = {reviewer:string;level:"community"|"specialist";scope:"language"|"full-original";date:string;evidenceUrl:string;sourceSha256:string;translationSha256:string};
export type Entry = {
  id:string;title:string;king:string;kingKo:string;year:number;reignYear:number;
  month:number;day:number;volume:number;ordinal:number;topics:string[];
  original:string;translation:string[];notes:{title:string;text:string}[];
  dateScope?:"month";leapMonth?:boolean;dayName?:string;keywords?:string[];
  sourceRetrieved:string;originalSha256:string;translationSha256:string;
  reviewStatus:"draft"|"community-reviewed"|"specialist-reviewed";reviews:Review[];
  provenance:{method:"ai-generated"|"ai-assisted"|"human";contributors:string[];model:string;created:string;updated:string;guidelineVersion:string;sourceSha256:string;license:string};
};
export type CatalogEntry=Pick<Entry,"id"|"title"|"king"|"year"|"month"|"day"|"leapMonth"|"dateScope"|"topics"|"reviewStatus">;
export type SearchResult={items:CatalogEntry[];total:number;offset:number;limit:number;nextOffset:number|null};
export const edition={version:project.edition,date:project.editionDate,target:project.pilotTarget};
export const reviewLabel=(e:Pick<Entry,"reviewStatus">)=>({draft:"Draft · Unreviewed","community-reviewed":"Community reviewed","specialist-reviewed":"Specialist reviewed"}[e.reviewStatus]);
export const sourceUrl=(e:Pick<Entry,"id">)=>`https://sillok.history.go.kr/id/${e.id}`;
export const entryDate=(e:Entry)=>`${e.reignYear===0?"Accession year":`Year ${e.reignYear}`}, ${e.leapMonth?"intercalary ":""}month ${e.month}${e.dateScope==="month"?"":`, day ${e.day}`}`;
export const citation=(e:Entry)=>`Veritable Records of ${e.king}, vol. ${e.volume}, ${entryDate(e).toLowerCase()}, entry ${e.ordinal} (${e.year}). National Institute of Korean History. ${sourceUrl(e)}. English translation: Open Sillok ${edition.version}, ${edition.date}; contributors ${e.provenance.contributors.join(", ")}; ${e.provenance.method}; ${e.reviewStatus==="draft"?"not independently reviewed":`${reviewLabel(e)} (${[...new Set(e.reviews.map(r=>r.scope))].join(", ")})`}. Translation revision ${e.translationSha256.slice(0,12)}. CC BY-SA 4.0.`;

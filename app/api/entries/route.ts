import {catalogSearch} from "@/lib/annals";
export function GET(request:Request){
  const p=new URL(request.url).searchParams;
  const offset=Number(p.get("offset")??0),limit=Number(p.get("limit")??30);
  if(!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>50||(p.get("q")?.length??0)>300)return Response.json({error:"Invalid search parameters"},{status:400});
  return Response.json(catalogSearch(p.get("q")??"",p.get("king")??"all",p.get("topic")??"all",offset,limit),{headers:{"Cache-Control":"public, max-age=60","X-Content-Type-Options":"nosniff"}});
}

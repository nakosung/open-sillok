import project from "@/project.json";
export {project};
export const repository: string|null = project.repository;
export const githubUrl = repository ? `https://github.com/${repository}` : null;
export const contributionPath=(id:string)=>`content/en/${id.slice(0,3)}/${id}.json`;
export const editUrl=(id:string)=>githubUrl?`${githubUrl}/edit/main/${contributionPath(id)}`:null;
export const historyUrl=(id:string)=>githubUrl?`${githubUrl}/commits/main/${contributionPath(id)}`:null;
export const claimUrl=(id:string)=>githubUrl?`${githubUrl}/issues/new?template=work.yml&title=${encodeURIComponent(`Work: ${id}`)}&article=${encodeURIComponent(id)}`:null;
export const issueUrl=(id:string)=>githubUrl?`${githubUrl}/issues/new?template=correction.yml&title=${encodeURIComponent(`Correction: ${id}`)}&article=${encodeURIComponent(id)}`:null;

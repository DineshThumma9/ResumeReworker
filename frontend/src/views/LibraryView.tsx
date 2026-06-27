import useSWR from "swr";
import { Folder, Loader2 } from "lucide-react";
import type { Resume } from "../schemas";
import { LibraryResumeCard } from "../components/LibraryResumeCard";
import { resumeApi } from "../apis/resumes";

export function LibraryView() {
  const {
    data: resumes = [],
    isLoading,
    mutate,
  } = useSWR<Resume[]>("resumes", () => resumeApi.list());

  const onDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this resume? This action cannot be undone.")) return;
    // Optimistic UI update
    mutate(
      resumes.filter((x) => x.id !== id),
      false,
    );
    try {
      await resumeApi.delete(id);
      mutate(); // Revalidate after delete
    } catch (e) {
      mutate(); // Rollback if error
      console.error(e);
    }
  };

  return (
    <div className="px-6 py-10 flex flex-col gap-6 overflow-y-auto h-full w-full">
      <div>
        <h1 className="font-heading text-3xl font-bold text-foreground">
          My Library
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          All your saved and tailored resumes.
        </p>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center text-muted-foreground">
          <Loader2 size={32} className="animate-spin" />
          <p className="font-medium">Loading library...</p>
        </div>
      ) : resumes.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
          <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center">
            <Folder
              size={32}
              strokeWidth={1}
              className="text-muted-foreground"
            />
          </div>
          <div>
            <p className="font-semibold text-foreground">No resumes yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Create one from the New Analysis tab.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumes.map((r) => (
            <LibraryResumeCard key={r.id} resume={r} onDelete={onDelete} />
          ))}
        </div>
      )}
    </div>
  );
}

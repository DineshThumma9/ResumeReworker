import { useState, useRef } from "react";
import useSWR from "swr";
import { Folder, Loader2 } from "lucide-react";
import type { Resume } from "../schemas";
import { LibraryResumeCard } from "../components/LibraryResumeCard";
import { resumeApi } from "../apis/resumes";
import { Button } from "../components/ui/button";
import { Plus } from "lucide-react";

export function LibraryView() {
  const {
    data: resumes = [],
    isLoading,
    mutate,
  } = useSWR<Resume[]>("resumes", () => resumeApi.list());

  const [deleteId, setDeleteId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileToAdd, setFileToAdd] = useState<File | null>(null);
  const [fileLabel, setFileLabel] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFileToAdd(file);
      setFileLabel(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleConfirmSave = async () => {
    if (!fileToAdd) return;
    setIsUploading(true);
    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const base64 = event.target?.result as string;
        try {
          await resumeApi.create(
            fileLabel || "Untitled",
            "",
            undefined,
            base64,
          );
          mutate(); // Revalidate library
          setFileToAdd(null);
          setFileLabel("");
          if (fileInputRef.current) {
            fileInputRef.current.value = "";
          }
        } catch (err) {
          console.error("Failed to upload resume:", err);
          alert("Failed to upload resume");
        } finally {
          setIsUploading(false);
        }
      };
      reader.readAsDataURL(fileToAdd);
    } catch (err) {
      console.error(err);
      setIsUploading(false);
    }
  };

  const onDelete = (id: number) => {
    setDeleteId(id);
  };

  const handleConfirmDelete = async () => {
    if (deleteId === null) return;
    const id = deleteId;
    setDeleteId(null);

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
  const handleRename = async (id: number, newLabel: string) => {
    mutate(
      resumes.map((x) => (x.id === id ? { ...x, label: newLabel } : x)),
      false,
    );
    try {
      await resumeApi.rename(id, newLabel);
      mutate();
    } catch (e) {
      mutate();
      console.error(e);
    }
  };

  return (
    <div className="px-4 py-6 md:px-6 md:py-10 flex flex-col gap-4 md:gap-6 overflow-y-auto h-full w-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sm:gap-0">
        <div>
          <h1 className="font-['EB_Garamond'] text-[36px] font-semibold text-foreground tracking-tight">
            My Library
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            All your saved and tailored resumes.
          </p>
        </div>
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
        />
        <Button
          onClick={() => {
            fileInputRef.current?.click();
          }}
          className="gap-2 w-full sm:w-auto"
        >
          <Plus className="w-4 h-4" />
          Add Resume
        </Button>
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
            <LibraryResumeCard
              key={r.id}
              resume={r}
              onDelete={onDelete}
              onRename={handleRename}
            />
          ))}
        </div>
      )}

      {/* DELETE CONFIRMATION MODAL */}
      {deleteId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-sm p-6 animate-in fade-in zoom-in-95 duration-200 text-center">
            <h3 className="font-['EB_Garamond'] text-2xl font-semibold mb-2">
              Delete Resume
            </h3>
            <p className="text-xs text-muted-foreground mb-6">
              Are you sure you want to delete this resume? This action cannot be
              undone.
            </p>
            <div className="flex justify-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDeleteId(null)}
              >
                Cancel
              </Button>
              <Button
                variant="default"
                size="sm"
                className="bg-red-600 hover:bg-red-700 text-white font-semibold"
                onClick={handleConfirmDelete}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
      {/* ADD RESUME MODAL */}
      {fileToAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-sm p-6 animate-in fade-in zoom-in-95 duration-200">
            <h3 className="font-['EB_Garamond'] text-2xl font-semibold mb-2">
              Save to Library
            </h3>
            <p className="text-xs text-muted-foreground mb-4">
              Do you want to save "{fileToAdd.name}" directly to your library?
            </p>
            <div className="mb-6">
              <label className="text-xs font-semibold text-muted-foreground mb-1 block">
                Label
              </label>
              <input
                type="text"
                className="w-full text-sm p-2 rounded-md border bg-background"
                value={fileLabel}
                onChange={(e) => setFileLabel(e.target.value)}
                disabled={isUploading}
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                size="sm"
                disabled={isUploading}
                onClick={() => {
                  setFileToAdd(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
              >
                Cancel
              </Button>
              <Button
                variant="default"
                size="sm"
                disabled={isUploading || !fileLabel.trim()}
                onClick={handleConfirmSave}
              >
                {isUploading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : null}
                Save Resume
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

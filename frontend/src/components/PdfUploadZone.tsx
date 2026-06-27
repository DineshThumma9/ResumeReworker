import { Input } from "./ui/input";

export function PdfUploadZone({
  file,
  onFile,
}: {
  file: File | null;
  onFile: (f: File | null) => void;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Input
        type="file"
        accept="application/pdf"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            onFile(e.target.files[0]);
          } else {
            onFile(null);
          }
        }}
        className="cursor-pointer file:cursor-pointer file:bg-primary file:text-primary-foreground file:border-0 file:rounded-md file:px-4 file:mr-4 hover:file:bg-primary/90"
      />
      {file && (
        <span className="text-xs text-muted-foreground mt-1">
          Selected: {file.name}
        </span>
      )}
    </div>
  );
}

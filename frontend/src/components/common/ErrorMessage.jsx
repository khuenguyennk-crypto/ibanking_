export default function ErrorMessage({message}) {
  if (!message) return null;
  return <p className="pay-error" role="alert"> {message} </p>;
}


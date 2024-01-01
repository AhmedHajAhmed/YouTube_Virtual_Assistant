from transformers import pipeline
from langchain.document_loaders import YoutubeLoader
import re




def get_video_transcript_from_url(video_url: str) -> str:
    """
    This function generates the transcript of a YouTube video
    :param video_url: a URL for a YouTube video
    :returns: a transcript of the YouTube video
    :raises ValueError: raises an exception if video URL is empty or invalid
    :raises RuntimeError: raises an exception video doesn't have a transcript
    """
    if not video_url:
        raise ValueError("Video URL cannot be empty.")
    youtube_pattern = re.compile(r'https://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)(\w+)')
    if not youtube_pattern.match(video_url):
        raise ValueError("Invalid or unsupported video URL.")
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()
    transcript = str(transcript)        # convert FAISS object into str
    if not transcript:
        raise RuntimeError("The video doesn't have a transcript.")
    return transcript


def clean_transcript(transcript: str) -> str:
    """
    This function cleans and preprocesses a given text
    :param transcript: a transcript string
    :returns: a cleaned version of transcript string
    :raises ValueError: raises an exception input is empty or if it consists of special characters
    """
    if not transcript:
        raise ValueError("Input text cannot be empty.")
    if re.match(r'^[!@#$%^&*(),.?":{}|<>_+=\[\];\'\\`~]*$', transcript):
        raise ValueError("Input text consists only of special characters.")
    transcript = re.sub(r'\[.*?\]', '', transcript)         # Remove square brackets and their contents
    transcript = re.sub(r'\\n', ' ', transcript)            # Replace newline characters with a space
    transcript = ' '.join(transcript.split())               # Remove extra spaces
    transcript = re.sub(r'[^\w\s.\']', '', transcript)      # Remove special characters excluding dots and apostrophes
    # transcript = re.sub(r'\s+(?=[A-Z])', '', transcript)    # Remove leading white spaces at the beginning of each sentence
    return transcript


def divide_transcript_into_sentences(transcript: str) -> list[str]:
    """
    This function divides transcript into sentences
    :param transcript: a transcript string
    :returns: a list consisting of sentences
    """
    transcript = clean_transcript(transcript)
    transcript = transcript.replace('.', '.<eos>')
    transcript = transcript.replace('?', '?<eos>')
    transcript = transcript.replace('!', '!<eos>')
    return transcript.split('<eos>')


def combine_sentences_into_chunks(sentences: list[str]) -> list[str]:
    """
    This function combines sentences into chunks with a maximum word limit of 512, set by the summerizer
    :param sentences: a list of sentences
    :returns: a list consisting of chunks of sentences
    """
    max_words = 512
    current_chunk = 0
    chunks = []

    for sentence in sentences:
        if len(chunks) == current_chunk + 1:
            if len(chunks[current_chunk]) + len(sentence.split(' ')) < max_words:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            print(current_chunk)
            chunks.append(sentence.split(' '))

    # join the words in each chunk back into a single string
    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])

    return chunks







# URL = "https://www.youtube.com/watch?v=rtgN27z0oi0"
URL = "https://www.youtube.com/watch?v=RR2DpT_Eie8"
transcript = get_video_transcript_from_url(URL)
sentences = divide_transcript_into_sentences(transcript)
chunks = combine_sentences_into_chunks(sentences)
for c in chunks:
    print(c)
    print(len(c.split()))
    print("\n")

summarizer = pipeline("summarization")
res = summarizer(chunks, max_length=150, min_length=5, do_sample=False)
print(len(res))
res = ' '.join([summ['summary_text'] for summ in res])
print(res)



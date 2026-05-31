//! Volc Engine streaming ASR ("bigmodel") binary wire protocol.
//!
//! Reference: <https://www.volcengine.com/docs/6561/1354869>
//!
//! ## Frame layout
//!
//! Every WebSocket binary frame is shaped:
//!
//! ```text
//! +------------------------+
//! | 4-byte fixed header    |
//! +------------------------+
//! | optional 4-byte seq    |   (only when flags has FLAG_HAS_SEQUENCE)
//! +------------------------+
//! | 4-byte payload length  |   (big-endian u32)
//! +------------------------+
//! | N bytes payload        |   (JSON / raw audio / gzipped JSON)
//! +------------------------+
//! ```
//!
//! ### 4-byte header
//!
//! | byte | bits 4–7                | bits 0–3              |
//! |------|-------------------------|-----------------------|
//! | 0    | protocol version (= 1)  | header size in 4-byte units (= 1) |
//! | 1    | message type            | message-type-specific flags        |
//! | 2    | serialization method    | compression method                 |
//! | 3    | reserved (0)            |                                    |
//!
//! ### Message types we care about
//!
//! | hex  | meaning                      | direction       |
//! |------|------------------------------|-----------------|
//! | 0x01 | full client request (JSON)   | client → server |
//! | 0x02 | audio-only request           | client → server |
//! | 0x09 | full server response         | server → client |
//! | 0x0B | server ack                   | server → client |
//! | 0x0F | server error                 | server → client |
//!
//! ### Flags (bits 0–3 of byte 1)
//!
//! | hex  | meaning                                               |
//! |------|-------------------------------------------------------|
//! | 0x00 | none                                                  |
//! | 0x01 | first packet                                          |
//! | 0x02 | last packet                                           |
//! | 0x03 | first AND last (single-shot)                          |
//! | 0x04 | "has sequence number" — payload prefixed with 4-byte i32 seq |
//!
//! Compression: 0x00 = none, 0x01 = gzip. We send `none`. We accept
//! `gzip` on receive (decompressed transparently).

use bytes::{Buf, BufMut, BytesMut};

// Header version + size
pub const PROTO_VERSION: u8 = 0x01;
pub const HEADER_SIZE_4B: u8 = 0x01;

// Message types
pub const MSG_FULL_CLIENT_REQUEST: u8 = 0x01;
pub const MSG_AUDIO_ONLY_REQUEST: u8 = 0x02;
pub const MSG_FULL_SERVER_RESPONSE: u8 = 0x09;
pub const MSG_SERVER_ERROR: u8 = 0x0F;

// Flags
pub const FLAG_NONE: u8 = 0x00;
pub const FLAG_FIRST: u8 = 0x01;
pub const FLAG_LAST: u8 = 0x02;
pub const FLAG_FIRST_AND_LAST: u8 = 0x03;
pub const FLAG_HAS_SEQUENCE: u8 = 0x04;

// Serialization
pub const SER_NONE: u8 = 0x00;
pub const SER_JSON: u8 = 0x01;

// Compression
pub const CMP_NONE: u8 = 0x00;
pub const CMP_GZIP: u8 = 0x01;

/// Encode a "full client request" carrying a JSON config payload.
pub fn encode_full_client_request(json: &[u8]) -> BytesMut {
    encode_message(
        MSG_FULL_CLIENT_REQUEST,
        FLAG_FIRST,
        SER_JSON,
        CMP_NONE,
        None,
        json,
    )
}

/// Encode an audio chunk. `is_last` makes this the EOS packet.
pub fn encode_audio_chunk(audio: &[u8], is_last: bool) -> BytesMut {
    let flags = if is_last { FLAG_LAST } else { FLAG_NONE };
    encode_message(
        MSG_AUDIO_ONLY_REQUEST,
        flags,
        SER_NONE,
        CMP_NONE,
        None,
        audio,
    )
}

fn encode_message(
    msg_type: u8,
    flags: u8,
    serialization: u8,
    compression: u8,
    sequence: Option<i32>,
    payload: &[u8],
) -> BytesMut {
    let extra = if sequence.is_some() { 4 } else { 0 };
    let mut buf = BytesMut::with_capacity(4 + extra + 4 + payload.len());

    buf.put_u8((PROTO_VERSION << 4) | HEADER_SIZE_4B);
    buf.put_u8((msg_type << 4) | flags);
    buf.put_u8((serialization << 4) | compression);
    buf.put_u8(0);

    if let Some(seq) = sequence {
        buf.put_i32(seq);
    }

    buf.put_u32(payload.len() as u32);
    buf.put_slice(payload);
    buf
}

/// Parsed view of an inbound frame from the Volc ASR server.
#[derive(Debug, Clone)]
pub struct ServerMessage {
    pub message_type: u8,
    pub flags: u8,
    /// Present when the server set `FLAG_HAS_SEQUENCE`. Negative seq = final.
    pub sequence: Option<i32>,
    pub serialization: u8,
    pub compression: u8,
    /// Raw payload bytes (already decompressed if gzipped).
    pub payload: Vec<u8>,
}

#[derive(Debug, thiserror::Error)]
pub enum ParseError {
    #[error("frame shorter than fixed header")]
    TooShort,
    #[error("unsupported protocol version {0}")]
    UnsupportedVersion(u8),
    #[error("declared header size {0} bytes is impossible")]
    BadHeaderSize(usize),
    #[error("missing sequence number ({needed} bytes, have {have})")]
    MissingSeq { needed: usize, have: usize },
    #[error("missing or truncated payload ({needed} bytes, have {have})")]
    TruncatedPayload { needed: usize, have: usize },
    #[error("unsupported compression: 0x{0:02x}")]
    UnsupportedCompression(u8),
    #[error("gzip decompression failed: {0}")]
    Gzip(String),
}

pub fn parse_server_message(bytes: &[u8]) -> Result<ServerMessage, ParseError> {
    if bytes.len() < 4 {
        return Err(ParseError::TooShort);
    }
    let mut cursor = bytes;
    let proto_ver = cursor[0] >> 4;
    let header_size_units = cursor[0] & 0x0F;
    let msg_type = cursor[1] >> 4;
    let flags = cursor[1] & 0x0F;
    let serialization = cursor[2] >> 4;
    let compression = cursor[2] & 0x0F;

    if proto_ver != PROTO_VERSION {
        return Err(ParseError::UnsupportedVersion(proto_ver));
    }

    let header_bytes = (header_size_units as usize) * 4;
    if header_bytes < 4 {
        return Err(ParseError::BadHeaderSize(header_bytes));
    }
    if bytes.len() < header_bytes {
        return Err(ParseError::TruncatedPayload {
            needed: header_bytes,
            have: bytes.len(),
        });
    }
    cursor = &cursor[header_bytes..];

    let sequence = if flags & FLAG_HAS_SEQUENCE != 0 {
        if cursor.len() < 4 {
            return Err(ParseError::MissingSeq {
                needed: 4,
                have: cursor.len(),
            });
        }
        Some(cursor.get_i32())
    } else {
        None
    };

    if cursor.len() < 4 {
        return Err(ParseError::TruncatedPayload {
            needed: 4,
            have: cursor.len(),
        });
    }
    let payload_size = cursor.get_u32() as usize;
    if cursor.len() < payload_size {
        return Err(ParseError::TruncatedPayload {
            needed: payload_size,
            have: cursor.len(),
        });
    }
    let payload_raw = cursor[..payload_size].to_vec();

    let payload = match compression {
        CMP_NONE => payload_raw,
        CMP_GZIP => decompress_gzip(&payload_raw)?,
        other => return Err(ParseError::UnsupportedCompression(other)),
    };

    Ok(ServerMessage {
        message_type: msg_type,
        flags,
        sequence,
        serialization,
        compression,
        payload,
    })
}

fn decompress_gzip(data: &[u8]) -> Result<Vec<u8>, ParseError> {
    use std::io::Read;
    let mut decoder = flate2::read::GzDecoder::new(data);
    let mut out = Vec::with_capacity(data.len() * 2);
    decoder
        .read_to_end(&mut out)
        .map_err(|e| ParseError::Gzip(e.to_string()))?;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn full_client_request_round_trips() {
        let json = br#"{"hello":"world"}"#;
        let frame = encode_full_client_request(json);

        // Header bytes
        assert_eq!(frame[0], (PROTO_VERSION << 4) | HEADER_SIZE_4B);
        assert_eq!(frame[1], (MSG_FULL_CLIENT_REQUEST << 4) | FLAG_FIRST);
        assert_eq!(frame[2], (SER_JSON << 4) | CMP_NONE);
        assert_eq!(frame[3], 0);

        // Payload size = 17, big-endian
        let size = u32::from_be_bytes([frame[4], frame[5], frame[6], frame[7]]);
        assert_eq!(size as usize, json.len());
        assert_eq!(&frame[8..], json.as_slice());
    }

    #[test]
    fn audio_chunk_marks_last() {
        let pcm = vec![0u8; 640];
        let frame = encode_audio_chunk(&pcm, true);
        assert_eq!(frame[1], (MSG_AUDIO_ONLY_REQUEST << 4) | FLAG_LAST);
    }

    #[test]
    fn parses_server_response_with_sequence() {
        // Construct a server frame: type=0x09, flags = FLAG_HAS_SEQUENCE, seq=42, payload=`{"text":"hi"}`
        let payload = br#"{"text":"hi"}"#;
        let mut bytes = BytesMut::new();
        bytes.put_u8((PROTO_VERSION << 4) | HEADER_SIZE_4B);
        bytes.put_u8((MSG_FULL_SERVER_RESPONSE << 4) | FLAG_HAS_SEQUENCE);
        bytes.put_u8((SER_JSON << 4) | CMP_NONE);
        bytes.put_u8(0);
        bytes.put_i32(42);
        bytes.put_u32(payload.len() as u32);
        bytes.put_slice(payload);

        let msg = parse_server_message(&bytes).unwrap();
        assert_eq!(msg.message_type, MSG_FULL_SERVER_RESPONSE);
        assert_eq!(msg.sequence, Some(42));
        assert_eq!(&msg.payload, payload.as_slice());
    }

    #[test]
    fn parses_negative_sequence_as_final_marker() {
        let payload = br#"{"text":"final"}"#;
        let mut bytes = BytesMut::new();
        bytes.put_u8((PROTO_VERSION << 4) | HEADER_SIZE_4B);
        bytes.put_u8((MSG_FULL_SERVER_RESPONSE << 4) | (FLAG_HAS_SEQUENCE | FLAG_LAST));
        bytes.put_u8((SER_JSON << 4) | CMP_NONE);
        bytes.put_u8(0);
        bytes.put_i32(-7);
        bytes.put_u32(payload.len() as u32);
        bytes.put_slice(payload);

        let msg = parse_server_message(&bytes).unwrap();
        assert!(msg.sequence.unwrap() < 0);
        assert!(msg.flags & FLAG_LAST != 0);
    }

    #[test]
    fn rejects_truncated_frame() {
        let bytes = vec![0x11, 0x91, 0x10, 0x00, 0x00, 0x00];
        assert!(matches!(
            parse_server_message(&bytes),
            Err(ParseError::TruncatedPayload { .. })
        ));
    }

    #[test]
    fn rejects_unknown_protocol_version() {
        let bytes = [0x21, 0x91, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00];
        assert!(matches!(
            parse_server_message(&bytes),
            Err(ParseError::UnsupportedVersion(2))
        ));
    }

    #[test]
    fn round_trip_through_gzip() {
        // Compress a JSON payload, frame it, parse it back.
        use flate2::write::GzEncoder;
        use flate2::Compression;
        use std::io::Write;
        let original = br#"{"text":"hello world"}"#;
        let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
        encoder.write_all(original).unwrap();
        let gzipped = encoder.finish().unwrap();

        let mut bytes = BytesMut::new();
        bytes.put_u8((PROTO_VERSION << 4) | HEADER_SIZE_4B);
        bytes.put_u8(MSG_FULL_SERVER_RESPONSE << 4);
        bytes.put_u8((SER_JSON << 4) | CMP_GZIP);
        bytes.put_u8(0);
        bytes.put_u32(gzipped.len() as u32);
        bytes.put_slice(&gzipped);

        let msg = parse_server_message(&bytes).unwrap();
        assert_eq!(msg.compression, CMP_GZIP);
        assert_eq!(&msg.payload, original.as_slice());
    }
}

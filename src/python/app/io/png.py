"""Module providing serialization and deserialization for PNG format (https://en.wikipedia.org/wiki/PNG)"""

import struct
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, astuple
from enum import IntEnum
from typing import final, BinaryIO, override, ClassVar, Sequence

import numpy as np

from app.error.invalid_format_exception import InvalidFormatException
from app.image.image import Image
from app.io.format_checker import IFormatChecker, check_compare
from app.io.format_reader import IFormatReader
from app.io.format_writer import IFormatWriter
from app.io.known_format import KnownFormat


@final
class PNGChecker(IFormatChecker):
    """Class checking if a given file starts with a PNG signature. Used for the type deduction"""

    @override
    def check_format(self, file: BinaryIO) -> bool:
        return check_compare(file, '89504E470D0A1A0A')

    @override
    def type(self) -> KnownFormat:
        return KnownFormat.PNG


@dataclass(slots=True, frozen=True)
class PNGSignature:
    """Implements the struct for the PNG file signature"""

    SIGNATURE_LENGTH: ClassVar[int] = 8
    START_TRANSMISSION_BYTE: ClassVar[int] = 0x89
    ASCII_P: ClassVar[int] = ord('P')
    ASCII_N: ClassVar[int] = ord('N')
    ASCII_G: ClassVar[int] = ord('G')
    DOS_CRLF: ClassVar[int] = 0x0D0A
    DOS_STOP_DISPLAY: ClassVar[int] = 0x1A
    UNIX_ENDING: ClassVar[int] = 0x0A

    start_transmission_byte: int
    signature_p: int
    signature_n: int
    signature_g: int
    dos_line_ending: int
    dos_stop_display: int
    unix_ending: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PNGSignature':
        """Additional constructor for PNG Signature form raw data bytes"""

        if len(data) < cls.SIGNATURE_LENGTH:
            raise InvalidFormatException(
                f"Signature too short, received: {len(data)} instead of {cls.SIGNATURE_LENGTH}"
            )

        return cls(*struct.unpack('>BBBBHBB', data))

    @classmethod
    def from_default(cls) -> 'PNGSignature':
        """Additional constructor for PNG Signature form default values"""

        return cls(start_transmission_byte=cls.START_TRANSMISSION_BYTE,
                   signature_p=cls.ASCII_P,
                   signature_n=cls.ASCII_N,
                   signature_g=cls.ASCII_G,
                   dos_line_ending=cls.DOS_CRLF,
                   dos_stop_display=cls.DOS_STOP_DISPLAY,
                   unix_ending=cls.UNIX_ENDING)

    def __post_init__(self) -> None:
        if self.start_transmission_byte != self.START_TRANSMISSION_BYTE:
            raise InvalidFormatException("Invalid signature")

        if self.signature_p != self.ASCII_P:
            raise InvalidFormatException("Invalid signature")

        if self.signature_n != self.ASCII_N:
            raise InvalidFormatException("Invalid signature")

        if self.signature_g != self.ASCII_G:
            raise InvalidFormatException("Invalid signature")

        if self.dos_line_ending != self.DOS_CRLF:
            raise InvalidFormatException("Invalid signature")

        if self.dos_stop_display != self.DOS_STOP_DISPLAY:
            raise InvalidFormatException("Invalid signature")

        if self.unix_ending != self.UNIX_ENDING:
            raise InvalidFormatException("Invalid signature")

    def __bytes__(self) -> bytes:
        return struct.pack('>BBBBHBB', *astuple(self))


class ChunkType(IntEnum):
    """https://en.wikipedia.org/wiki/PNG#%22Chunks%22_within_the_file"""

    # pylint: disable=invalid-name
    IHDR = 0x49484452
    PLTE = 0x504C5445
    IDAT = 0x49444154
    IEND = 0x49454E44

    tRNS = 0x74524E53
    cHRM = 0x6348524D
    gAMA = 0x67414D41
    iCCP = 0x69434350
    sBIT = 0x73424954
    sRGB = 0x73524742
    cICP = 0x63494350
    mDCV = 0x6D444356
    cLLI = 0x634C4C49

    tEXt = 0x74455874
    zTXt = 0x7A545874
    iTXt = 0x69545874

    bKGD = 0x624B4744
    hIST = 0x68495354
    pHYs = 0x70485973
    sPLT = 0x73504C54
    eXIf = 0x65584966
    tIME = 0x74494D45
    acTL = 0x6163544C
    fcTL = 0x6663544C
    fdAT = 0x66644154

    @classmethod
    def map_data_to_chunk_type(cls, data: bytes) -> 'ChunkType':
        """Additional constructor that converts the 4 bytes of the type to a ChunkType enum"""

        return cls(*struct.unpack('>I', data))

    def map_chunk_type_to_data_class(self):
        """Convert the Chunk type to a class that will handle parsing of the chunk data filed"""

        match self:
            case ChunkType.IHDR:
                return IHDRData

            case ChunkType.PLTE:
                return PLTEData

            case ChunkType.IDAT:
                return IDATData

            case ChunkType.IEND:
                return IENDData

            case _:
                return NotCriticalData


class IChunkDataTypeSerializer(ABC):
    """Interface for the Chunk data serialization"""

    @abstractmethod
    def type(self) -> ChunkType:
        """Method that returns the Chunk type the serializer can parse"""

    @abstractmethod
    def __bytes__(self) -> bytes:
        pass


@dataclass(slots=True, frozen=True)
class IHDRData(IChunkDataTypeSerializer):
    """IHDR"""

    DATA_LENGTH: ClassVar[int] = 13

    DEFLATE_COMPRESSION: ClassVar[int] = 0

    FILTER_METHOD: ClassVar[int] = 0

    WITH_NO_INTERLACE: ClassVar[int] = 0
    WITH_INTERLACE_ADAM7: ClassVar[int] = 1

    width: int
    height: int
    bit_depth: int
    color_type: int
    compression_method: int
    filter_method: int
    interlace_method: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'IHDRData':
        """Additional constructor for the class that allows the object creation from the raw data"""

        if len(data) < cls.DATA_LENGTH:
            raise InvalidFormatException(f"Header too short, received: {len(data)} instead of {cls.DATA_LENGTH}")

        return cls(*struct.unpack('>IIBBBBB', data))

    @classmethod
    def from_numpy(cls, data: np.ndarray) -> 'IHDRData':
        """Additional constructor for the class that allows the object creation from the raw data"""

        return cls(width=data.shape[1],
                   height=data.shape[0],
                   bit_depth=16 if data.dtype == np.uint16 else 8,
                   color_type=6,
                   compression_method=cls.DEFLATE_COMPRESSION,
                   filter_method=cls.FILTER_METHOD,
                   interlace_method=cls.WITH_NO_INTERLACE)

    @override
    def type(self) -> ChunkType:
        return ChunkType.IHDR

    def __bytes__(self) -> bytes:
        return struct.pack('>IIBBBBB', *astuple(self))

    def __post_init__(self) -> None:
        if self.bit_depth not in {1, 2, 4, 8, 16}:
            raise InvalidFormatException("Invalid IHDR")


@dataclass(slots=True, frozen=True)
class PLTEData(IChunkDataTypeSerializer):
    """PLTE"""

    palette_entries: np.ndarray

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PLTEData':
        """Additional constructor for the class that allows the object creation from the raw data"""

        length, remainder = divmod(len(data), 3)
        if remainder != 0:
            raise InvalidFormatException("Wrong Palette")

        return cls(palette_entries=np.frombuffer(data, dtype=np.uint8).reshape((length, 3)))

    @override
    def type(self) -> ChunkType:
        return ChunkType.PLTE

    def __bytes__(self) -> bytes:
        return self.palette_entries.tobytes()

    def __post_init__(self) -> None:
        if len(self.palette_entries.shape) != 2:
            raise InvalidFormatException("Wrong Palette")

        if 1 <= self.palette_entries.shape[0] <= 256:
            raise InvalidFormatException("Wrong Palette")

        if self.palette_entries.shape[1] == 3:
            raise InvalidFormatException("Wrong Palette")


@dataclass(slots=True, frozen=True)
class IDATData(IChunkDataTypeSerializer):
    """IDAT"""

    compressed_data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> 'IDATData':
        """Serializer (additional constructor) that takes bytes"""

        return cls(compressed_data=data)

    @classmethod
    def from_numpy(cls, data: np.ndarray) -> 'IDATData':
        """Serialize for IDAT binary content"""

        new_data = np.concatenate((data, np.full((data.shape[0], data.shape[1], 1), 255, dtype=np.uint8)), axis=2)

        stream = bytearray()
        compressor = zlib.compressobj(level=zlib.Z_BEST_SPEED)

        for i in range(new_data.shape[0]):
            stream += compressor.compress(b'\0' + new_data[i].tobytes())

        stream += compressor.flush()

        return cls(compressed_data=bytes(stream))

    @override
    def type(self) -> ChunkType:
        return ChunkType.IDAT

    def __bytes__(self) -> bytes:
        return self.compressed_data


@dataclass(slots=True, frozen=True)
class IENDData(IChunkDataTypeSerializer):
    """IEND"""

    @classmethod
    def from_bytes(cls, data: bytes) -> 'IENDData':
        """Additional constructor that serialize the IEND chunk"""

        if len(data) != 0:
            raise InvalidFormatException("Data must be empty")

        return cls()

    @override
    def type(self) -> ChunkType:
        return ChunkType.IEND

    def __bytes__(self) -> bytes:
        return b''


@dataclass(slots=True, frozen=True)
class NotCriticalData(IChunkDataTypeSerializer):
    """Other"""

    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> 'NotCriticalData':
        """Identity additional constructor for that that can be ignored"""
        return cls(data=data)

    @override
    def type(self) -> ChunkType:
        return ChunkType.IEND

    def __bytes__(self) -> bytes:
        return self.data


@dataclass(slots=True, frozen=True)
class PNGChunk[T: IChunkDataTypeSerializer]:
    """Class representing the whole chunk from the PNG file. (One chunk of many)"""

    length: int
    chunk_type: ChunkType
    chunk_data: T
    crc: int

    @classmethod
    def from_file(cls, data: bytes) -> tuple['PNGChunk', bytes]:
        """Additional constructor that creates the chunk from binary data."""

        length, = struct.unpack('>I', data[:4])
        chunk_type = ChunkType.map_data_to_chunk_type(data[4:8])
        chunk_data = data[8:8 + length]
        crc, = struct.unpack('!I', data[8 + length:8 + 4 + length])
        rest = data[8 + 4 + length:]

        return PNGChunk(length=length,
                        chunk_type=chunk_type,
                        chunk_data=chunk_type.map_chunk_type_to_data_class().from_bytes(chunk_data),
                        crc=crc), rest

    @classmethod
    def from_chunk[U: IChunkDataTypeSerializer](cls, chunk: U) -> 'PNGChunk[U]':
        """Additional constructor that creates the chunk from chunk binary data."""
        chunk_bytes_data = bytes(chunk)
        chunk_length = len(chunk_bytes_data)
        chunk_type = chunk.type()
        chunk_crc = zlib.crc32(struct.pack('>I', chunk_type.value) + chunk_bytes_data)

        return PNGChunk(length=chunk_length,
                        chunk_type=chunk_type,
                        chunk_data=chunk,
                        crc=chunk_crc)

    def __post_init__(self) -> None:
        if self.crc != zlib.crc32(struct.pack('>I', self.chunk_type.value) + bytes(self.chunk_data)):
            raise InvalidFormatException("CRC check sum is invalid")

        if len(bytes(self.chunk_data)) != self.length:
            raise InvalidFormatException("Chunk data is wrong")

    def __bytes__(self) -> bytes:
        return struct.pack('>II', self.length, self.chunk_type.value) \
            + bytes(self.chunk_data) \
            + struct.pack('>I', self.crc)


@dataclass(slots=True)
class PNG:
    """Class representing the PNG file structure"""

    signature: PNGSignature
    i_header: PNGChunk[IHDRData]
    chunks: Sequence[PNGChunk]

    @classmethod
    def from_file(cls, file: BinaryIO) -> 'PNG':
        """Additional constructor for the PNG object that takes BinaryIO"""

        signature = PNGSignature.from_bytes(file.read(PNGSignature.SIGNATURE_LENGTH))
        all_data = file.read()
        chunks = []

        i_header, all_data = PNGChunk.from_file(all_data)

        while len(all_data) > 0:
            chunk, all_data = PNGChunk.from_file(all_data)
            chunks.append(chunk)

        return cls(signature=signature,
                   i_header=i_header,
                   chunks=chunks)

    @classmethod
    def from_numpy(cls, data: np.ndarray) -> 'PNG':
        """Additional constructor for the PNG object that takes numpy array"""

        i_header_chunk = IHDRData.from_numpy(data)
        data_chunk = IDATData.from_numpy(data)
        end_chunk = IENDData()

        return cls(signature=PNGSignature.from_default(),
                   i_header=PNGChunk.from_chunk(i_header_chunk),
                   chunks=[PNGChunk.from_chunk(data_chunk),
                           PNGChunk.from_chunk(end_chunk)])

    def __post_init__(self) -> None:
        if self.chunks[-1].chunk_type != ChunkType.IEND:
            raise InvalidFormatException("Last chunk is not end")

    def to_numpy(self) -> np.ndarray:
        """Serializer of the data to a numpy array"""
        all_data_compressed = b''.join(x.chunk_data.compressed_data
                                       for x in self.chunks
                                       if x.chunk_type == ChunkType.IDAT)
        result = zlib.decompress(all_data_compressed)

        palette = [x.chunk_data.palette_entries for x in self.chunks if x.chunk_type == ChunkType.PLTE]

        if len(palette) == 1:
            return palette[np.frombuffer(result)].reshape(self.i_header.chunk_data.height,
                                                          self.i_header.chunk_data.width,
                                                          3)

        image_channels: int = 4
        row_size = image_channels * self.i_header.chunk_data.width + 1

        stream = bytearray()
        for i in range(self.i_header.chunk_data.height):
            stream += result[1 + i * row_size: (i + 1) * row_size]

        return np.frombuffer(stream, dtype=np.uint8).reshape(self.i_header.chunk_data.height,
                                                             self.i_header.chunk_data.width,
                                                             4)[:, :, :-1]

    def to_file(self, file: BinaryIO) -> None:
        """Serializes the object to a BinaryIO interface"""

        file.write(bytes(self.signature))
        file.write(bytes(self.i_header))
        for chunk in self.chunks:
            file.write(bytes(chunk))


@final
class PNGReader(IFormatReader):     # pylint: disable=too-few-public-methods
    """Class that deserializes PNG format to Image"""

    @override
    def read_format(self, file: BinaryIO) -> Image:
        png = PNG.from_file(file)
        return Image(data=png.to_numpy())


@final
class PNGWriter(IFormatWriter):     # pylint: disable=too-few-public-methods
    """Class that serializes Image to PNG format"""

    @override
    def write_format(self, file: BinaryIO, input_image: Image) -> None:
        png = PNG.from_numpy(input_image.data)
        return png.to_file(file)

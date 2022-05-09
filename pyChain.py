# Imports
from email.policy import default
from numpy import record
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib

# Defining a Record Data Class


@dataclass
class Record:
    sender: str
    receiver: str
    amount: float


# Defining a Block Data Class
@dataclass
class Block:
    record: Record
    creator_id: int        # The id of the creator of the block
    prev_hash: str = "0"   # The hash of the previous block
    timestamp: str = datetime.datetime.utcnow().strftime(
        "%H:%M:%S")   # The time the block was created
    nonce: int = 0

    def hash_block(self):
        sha = hashlib.sha256()      # defining sha variable as a hashlib object

        # converting the record data to a string
        record = str(self.record).encode()
        # updating the sha object with the record data
        sha.update(record)

        # converting the creator id to a string
        creator_id = str(self.creator_id).encode()
        # updating the sha object with the creator id
        sha.update(creator_id)

        # converting the timestamp to a string
        timestamp = str(self.timestamp).encode()
        # updating the sha object with the timestamp
        sha.update(timestamp)

        # converting the previous hash to a string
        prev_hash = str(self.prev_hash).encode()
        # updating the sha object with the previous hash
        sha.update(prev_hash)

        # converting the nonce to a string
        nonce = str(self.nonce).encode()
        # updating the sha object with the nonce
        sha.update(nonce)

        return sha.hexdigest()


@dataclass
class PyChain:
    chain: List[Block]
    difficulty: int = 4   # The difficulty of the block chain

    def proof_of_work(self, block):
        calculated_hash = block.hash_block()    # defining the calculated hash

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1            # incrementing the nonce

            calculated_hash = block.hash_block()    # recalculating the hash

        print("Winning Hash", calculated_hash)
        return block

    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is not valid")

                return False
            block_hash = block.hash_block()

        print("Blockchain is valid")
        return True

################################################################################################################################################
# Streamlit Code


# Adds the cache decorator for Streamlit
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain...")
    return PyChain([Block("Genesis", 0)])


st.markdown("# PyChain")
st.markdown("## Store the Transaction Record in the PyChain")

pychain = setup()


# Add Relevent User Inputs to the Streamlit Interface
# Input area to get value for `sender` from user
sender = st.text_input("Enter the sender's name:")

# Input area to get value for `receiver` from user
receiver = st.text_input("Enter the receiver's name:")

# Input area to get value for `amount` from user
amount = st.text_input("Enter the amount:")

if st.button("Add Block"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    new_block = Block(
        record=Record(sender, receiver, amount),
        creator_id=42,
        prev_hash=prev_block_hash
    )

    pychain.add_block(new_block)
    st.balloons()


st.markdown("## The PyChain Ledger")
pychain_df = pd.DataFrame(pychain.chain).astype(str)
st.write(pychain_df)

difficulty = st.sidebar.slider("Block Difficulty", 1, 5, 2)
pychain.difficulty = difficulty

st.sidebar.write("# Block Inspector")
selected_block = st.sidebar.selectbox(
    "Which block would you like to see?", pychain.chain
)

st.sidebar.write(selected_block)

if st.button("Validate Chain"):
    st.write(pychain.is_valid())

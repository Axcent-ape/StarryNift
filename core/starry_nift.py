from core.utils import Web3Utils
from fake_useragent import UserAgent
import aiohttp


class StarryNift:
    def __init__(self, key: str, referral_link: str, bnb_rpc: str, proxy: str):
        self.referral_code = referral_link.split('=')[1]
        self.ABI = "[{\"inputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"user\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"date\",\"type\":\"uint256\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"consecutiveDays\",\"type\":\"uint256\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"rewardXP\",\"type\":\"uint256\"}],\"name\":\"UserSignedIn\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"admin\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"user\",\"type\":\"address\"}],\"name\":\"getConsecutiveSignInDays\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"user\",\"type\":\"address\"}],\"name\":\"getLastSignInDate\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"day\",\"type\":\"uint256\"}],\"name\":\"getRewardXP\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"getSignInInterval\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"user\",\"type\":\"address\"}],\"name\":\"getTimeUntilNextSignIn\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"user\",\"type\":\"address\"}],\"name\":\"hasBrokenStreak\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"setDefaultRewards\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"_maxDays\",\"type\":\"uint256\"}],\"name\":\"setMaxConsecutiveDays\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"_interval\",\"type\":\"uint256\"}],\"name\":\"setSignInInterval\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"day\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"rewardXP\",\"type\":\"uint256\"}],\"name\":\"setSignInReward\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"signIn\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"day\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"reward\",\"type\":\"uint256\"}],\"name\":\"updateSignReward\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"
        self.web3_utils = Web3Utils(key=key, http_provider=bnb_rpc)
        self.proxy = f"http://{proxy}" if proxy is not None else None

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": "Bearer null",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.starrynift.art",
            "Origin": "https://starrynift.art",
            "Referer": "https://starrynift.art/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": UserAgent(os='windows').random,
        }

        self.session = aiohttp.ClientSession(
            headers=headers,
            trust_env=True
        )

    async def login(self):
        signature = self.web3_utils.get_signed_code(await self.get_signature_msg())

        json_data = {
            "address": self.web3_utils.acct.address,
            "signature": signature,
            "referralCode": self.referral_code,
            "referralSource": 0
            }

        resp = await self.session.post(url='https://api.starrynift.art/api-v2/starryverse/auth/wallet/evm/login', json=json_data, proxy=self.proxy)

        auth_token = (await resp.json()).get("token")
        if auth_token:
            self.upd_login_token(token=auth_token)

        return bool(auth_token)

    async def get_signature_msg(self):
        url = f"https://api.starrynift.art/api-v2/starryverse/auth/wallet/challenge?address={self.web3_utils.acct.address}"

        resp = await self.session.get(url=url, proxy=self.proxy)
        return (await resp.json()).get('message')

    async def check_minted_pass(self):
        return self.web3_utils.balance_of_erc721(address=self.web3_utils.acct.address, contract_address='0xe364a4b0188ab22dc13718993b0fa0ca5f123edc')

    async def mint_pass(self, logger, thread, gas_price):
        signature = await self.get_mint_signature()

        to = "0xC92Df682A8DC28717C92D7B5832376e6aC15a90D"
        from_ = self.web3_utils.acct.address
        data = f"0xf75e03840000000000000000000000000000000000000000000000000000000000000020000000000000000000000000{from_[2:].lower()}000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000041{signature[2:]}00000000000000000000000000000000000000000000000000000000000000"
        gas_limit = 250000
        chain_id = 56

        status, tx_hash = self.web3_utils.send_data_tx(to=to, from_=from_, data=data, gas_price=self.web3_utils.w3.to_wei(gas_price, 'gwei'), gas_limit=gas_limit, chain_id=chain_id)

        if status:
            if await self.send_mint_hash(tx_hash):
                logger.success(f"Поток {thread} | Успешно сминтил пасс: {self.web3_utils.acct.address}: {tx_hash}")
        else: logger.error(f"Поток {thread} | Не смог сминтить пасс: {self.web3_utils.acct.address}: {tx_hash}")

    async def send_mint_hash(self, tx_hash):
        json_data = {
            'txHash': tx_hash
            }

        resp = await self.session.post('https://api.starrynift.art/api-v2/webhook/confirm/citizenship/mint', json=json_data, proxy=self.proxy)
        return (await resp.json()).get('ok') == 1

    async def get_mint_signature(self):
        json_data = {
            "category": 1
            }

        resp = await self.session.post('https://api.starrynift.art/api-v2/citizenship/citizenship-card/sign', json=json_data, proxy=self.proxy)
        return (await resp.json()).get('signature')

    async def daily_claim(self, logger, thread, gas_price):
        to = "0xE3bA0072d1da98269133852fba1795419D72BaF4"
        from_ = self.web3_utils.acct.address
        data = "0x9e4cda43"
        gas_limit = 90000
        chain_id = 56

        status, tx_hash = self.web3_utils.send_data_tx(to=to, from_=from_, data=data, gas_price=self.web3_utils.w3.to_wei(gas_price, 'gwei'), gas_limit=gas_limit, chain_id=chain_id)
        if status:
            if await self.send_daily_hash(tx_hash):
                logger.success(f"Поток {thread} | Заклеймил поинты: {self.web3_utils.acct.address}: {tx_hash}")
        else: logger.error(f"Поток {thread} | Не Заклеймил поинты: {self.web3_utils.acct.address}: {tx_hash}")

    async def send_daily_hash(self, tx_hash):
        json_data = {
            "txHash": tx_hash
        }

        resp = await self.session.post('https://api.starrynift.art/api-v2/webhook/confirm/daily-checkin/checkin', json=json_data, proxy=self.proxy)
        return (await resp.json()).get('ok') == 1

    async def get_daily_claim_time(self):
        contract = self.web3_utils.w3.eth.contract(address=self.web3_utils.w3.to_checksum_address('0xe3ba0072d1da98269133852fba1795419d72baf4'), abi=self.ABI)
        return contract.functions.getTimeUntilNextSignIn(self.web3_utils.acct.address).call()

    async def logout(self):
        await self.session.close()

    def upd_login_token(self, token: str):
        self.session.headers["Authorization"] = f"Bearer {token}"

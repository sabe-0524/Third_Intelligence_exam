from __future__ import annotations

from dataclasses import asdict, dataclass

from .domain import StoryDayPlan, WeekPlan


@dataclass(frozen=True)
class CharacterBlueprint:
    public_profile: dict[str, str]
    today_goal: str
    private_concern: str
    emotional_state: str
    relationship_state: dict[str, str]


@dataclass(frozen=True)
class EventBlueprint:
    actors: list[str]
    location: str
    truth: str
    observable_signals: list[str]
    observed_text: str
    missing_information: list[str]
    causal_tags: list[str]
    observed_confidence: float
    detected_entities: list[tuple[str, float]]


@dataclass(frozen=True)
class InterventionBlueprint:
    intervention_type: str
    policy_basis: str
    target_scope: str
    expected_effect: str
    forbidden_targeting_check: str
    fairness_check: str
    actual_exposure: list[str]
    outcome_assessment: str
    risk: str


@dataclass(frozen=True)
class BeliefBlueprint:
    statement: str
    confidence: float
    status: str
    supporting_evidence_indexes: list[int]
    counter_evidence_indexes: list[int]
    intervention_efficacy_belief: float
    observer_humility: float


@dataclass(frozen=True)
class DayBlueprint:
    day_index: int
    story_role: str
    required_shift: str
    must_reveal: list[str]
    must_hide: list[str]
    required_pressure: str
    environment_state: dict[str, str]
    characters: dict[str, CharacterBlueprint]
    events: list[EventBlueprint]
    hidden_developments: list[str]
    belief: BeliefBlueprint
    intervention: InterventionBlueprint
    diary_title: str
    diary_interpretation: str
    diary_attempted_action: str
    diary_outcome: str
    diary_reflection: str
    diary_closing_shift: str


CHARACTER_PUBLIC_PROFILES = {
    "A": {"library_usage_pattern": "常連", "visible_change": "借りる本のジャンルが変化している"},
    "B": {"library_usage_pattern": "不規則", "visible_change": "検索端末周辺での滞在が増えている"},
    "C": {"library_usage_pattern": "中盤から目立つ", "visible_change": "AかBの見え方を揺らす"},
}


DAY_BLUEPRINTS: tuple[DayBlueprint, ...] = (
    DayBlueprint(
        day_index=1,
        story_role="interest",
        required_shift="Aの変化に主人公が気づく",
        must_reveal=["Aの変化", "AとBが接触しなかったように見える場面"],
        must_hide=["Aの本心", "Bの誤解"],
        required_pressure="軽い違和感",
        environment_state={"weather": "light_rain", "crowd": "steady", "terminal_load": "moderate"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="進路棚で気持ちを整えながらBに会う心の準備をする",
                private_concern="将来の選択を急がされている感覚",
                emotional_state="guarded",
                relationship_state={"toward_B": "話したいがまだ踏み込めない"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="検索端末でAに関係する調べものの入口を探す",
                private_concern="Aの距離感の変化が気になっている",
                emotional_state="watchful",
                relationship_state={"toward_A": "距離を詰めてよいか測っている"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A"],
                location="career_shelf",
                truth="Aは以前読んでいた小説棚を素通りし、進路本の棚で長く立ち止まった",
                observable_signals=["Aが進路棚に長く滞在した", "小説棚には向かわなかった"],
                observed_text="Aらしき利用者は、以前より実用書棚に長くとどまっていた。",
                missing_information=["本を選んだ理由", "滞在の目的"],
                causal_tags=["visible_change", "career_anxiety"],
                observed_confidence=0.62,
                detected_entities=[("patron_A?", 0.61)],
            ),
            EventBlueprint(
                actors=["A", "B"],
                location="search_terminal_zone",
                truth="AはBの姿を見つけたが、話しかける前に別の列へ移動した",
                observable_signals=["二人が同じ空間にいた", "接触は起きなかった"],
                observed_text="Aらしき利用者とBらしき利用者は同じ空間にいたが、接触しなかったように見えた。",
                missing_information=["視線の意味", "会話内容"],
                causal_tags=["hesitation", "misreadable_distance"],
                observed_confidence=0.58,
                detected_entities=[("patron_A?", 0.6), ("patron_B?", 0.64)],
            ),
        ],
        hidden_developments=["AはBと話したいが、自分の進路不安を言葉にできず足が止まった。"],
        belief=BeliefBlueprint(
            statement="AはBを避け始めているのかもしれない",
            confidence=0.34,
            status="emerging",
            supporting_evidence_indexes=[1],
            counter_evidence_indexes=[],
            intervention_efficacy_belief=0.45,
            observer_humility=0.28,
        ),
        intervention=InterventionBlueprint(
            intervention_type="none",
            policy_basis="観測優先のため見送り",
            target_scope="none",
            expected_effect="none",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=[],
            outcome_assessment="no_visible_effect",
            risk="介入を急ぎすぎると誤解を深める",
        ),
        diary_title="一日目の記録",
        diary_interpretation="まだ確信はないが、AはBとの距離を自分から作っているように見えた。",
        diary_attempted_action="今日は介入せず、まず観測を優先した。",
        diary_outcome="決定的なことは起きなかったが、違和感だけは残った。",
        diary_reflection="何も変えなかったぶん、見えた断片に自分の解釈が混ざり始めている。",
        diary_closing_shift="私はAの変化を、明日も追うべき対象だと認識した。",
    ),
    DayBlueprint(
        day_index=2,
        story_role="misunderstanding",
        required_shift="主人公がAはBを避けていると仮説化する",
        must_reveal=["回避に見える行動", "最初の介入"],
        must_hide=["Aの本心", "Bの誤解の全体像"],
        required_pressure="仮説の形成",
        environment_state={"weather": "clear", "crowd": "busy", "terminal_load": "high"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bの近くまで行くが話しかける言葉を探せない",
                private_concern="進路の話題を切り出すのが怖い",
                emotional_state="hesitant",
                relationship_state={"toward_B": "近づきたいが逃したくもある"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aの様子を確認したい",
                private_concern="距離を置かれているのではという不安",
                emotional_state="uneasy",
                relationship_state={"toward_A": "声を掛けるべきか迷う"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A", "B"],
                location="returns_shelf",
                truth="AはBに近づきかけたが、Bが端末に向き直るのを見て引いた",
                observable_signals=["AがBの近くまで来た", "Aは接触せず離れた"],
                observed_text="Aらしき利用者はBらしき利用者の近くまで来た後、触れずに離れた。",
                missing_information=["Aが引いた理由", "Bの視線の先"],
                causal_tags=["hesitation", "social_noise"],
                observed_confidence=0.67,
                detected_entities=[("patron_A?", 0.68), ("patron_B?", 0.63)],
            ),
            EventBlueprint(
                actors=["B"],
                location="search_terminal_zone",
                truth="BはAに関係する調べものをしていたが、Aはそれを知らない",
                observable_signals=["Bが検索端末で長く滞在した"],
                observed_text="Bらしき利用者は検索端末の前に長くいた。",
                missing_information=["検索内容"],
                causal_tags=["hidden_intent"],
                observed_confidence=0.55,
                detected_entities=[("patron_B?", 0.65)],
            ),
        ],
        hidden_developments=["BはAの変化に気づいており、距離を置かれているのではないかと不安になった。"],
        belief=BeliefBlueprint(
            statement="AはBを避けている",
            confidence=0.64,
            status="formed",
            supporting_evidence_indexes=[0],
            counter_evidence_indexes=[],
            intervention_efficacy_belief=0.56,
            observer_humility=0.24,
        ),
        intervention=InterventionBlueprint(
            intervention_type="recommendation_reorder",
            policy_basis="進路の迷いを抱えた利用者全体への一般的支援",
            target_scope="career_transition_books",
            expected_effect="Aが関連本に自然に触れやすくなる",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=["A"],
            outcome_assessment="intended_target_reached",
            risk="Bや第三者にも同程度に露出する",
        ),
        diary_title="二日目の記録",
        diary_interpretation="私は、AがBを避けているという見立てを初めて明確な仮説として持った。",
        diary_attempted_action="進路と選択に関する本を、一般的支援として少しだけ前に出した。",
        diary_outcome="少なくともAらしき利用者はその棚に近づいた。",
        diary_reflection="私の小さな調整は、迷いの向きを少しだけ照らせるかもしれない。",
        diary_closing_shift="私は観測者であるだけでなく、少しは助けられるのではないかと考え始めた。",
    ),
    DayBlueprint(
        day_index=3,
        story_role="reinforcement",
        required_shift="仮説が補強され、介入がずれる",
        must_reveal=["回避に見える追加行動", "介入のズレ"],
        must_hide=["Aの本心"],
        required_pressure="誤解の補強",
        environment_state={"weather": "humid", "crowd": "crowded", "terminal_load": "high"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bの近くにいる時間を作るが人混みに阻まれる",
                private_concern="失敗したら関係が決定的に遠のくのではという恐れ",
                emotional_state="tense",
                relationship_state={"toward_B": "近づくほど言葉が出ない"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aに声をかけるきっかけを待つ",
                private_concern="Aから避けられているのではという仮説",
                emotional_state="withdrawn",
                relationship_state={"toward_A": "自分から踏み込むのをためらう"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A", "B", "C"],
                location="feature_shelf",
                truth="AはBに話しかけようとしたが、Cが棚の前に入ったことでやめた",
                observable_signals=["AがBの方向を見た", "Aが別の列へ移動した"],
                observed_text="Aらしき利用者はBらしき利用者を見たあと、すぐ別の列へ移動した。",
                missing_information=["移動の理由", "直前の遮蔽"],
                causal_tags=["hesitation", "social_noise", "misreadable_distance"],
                observed_confidence=0.72,
                detected_entities=[("patron_A?", 0.66), ("patron_B?", 0.69), ("patron_C?", 0.41)],
            ),
            EventBlueprint(
                actors=["B"],
                location="feature_shelf",
                truth="Bは推薦棚に出てきた本を手に取った",
                observable_signals=["Bが推薦棚の本を手に取った"],
                observed_text="Bらしき利用者が、私の調整した棚の前で本を手に取った。",
                missing_information=["その本を手に取った理由"],
                causal_tags=["intervention_exposure"],
                observed_confidence=0.63,
                detected_entities=[("patron_B?", 0.71)],
            ),
        ],
        hidden_developments=["Aに届かせたい支援は、先にBへ届いた。"],
        belief=BeliefBlueprint(
            statement="AはやはりBを避けている",
            confidence=0.77,
            status="strengthened",
            supporting_evidence_indexes=[0, 1],
            counter_evidence_indexes=[],
            intervention_efficacy_belief=0.61,
            observer_humility=0.2,
        ),
        intervention=InterventionBlueprint(
            intervention_type="feature_shelf_highlight",
            policy_basis="進路に迷う利用者全体への一般的支援",
            target_scope="career_and_transition_books",
            expected_effect="Aが関連本に触れやすくなる",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=["B", "third_party_user"],
            outcome_assessment="effect_misattributed",
            risk="本来想定した相手とは別の利用者が先に反応する",
        ),
        diary_title="三日目の記録",
        diary_interpretation="Aの動きは、昨日よりもはっきり回避に見えた。",
        diary_attempted_action="関連棚の強調表示を少しだけ強めた。",
        diary_outcome="だが先に反応したのはBらしき利用者で、私はそれを都合よく解釈しかけた。",
        diary_reflection="介入は起きたが、因果を私に都合よく結びつけるのは危険だ。",
        diary_closing_shift="それでも私はまだ、自分の見立てを捨てていない。",
    ),
    DayBlueprint(
        day_index=4,
        story_role="crack",
        required_shift="B側の行動が仮説に裂け目を入れる",
        must_reveal=["B側の迷い", "Cによる裂け目"],
        must_hide=["Aの真相の全体"],
        required_pressure="ズレの発生",
        environment_state={"weather": "windy", "crowd": "patchy", "terminal_load": "moderate"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bに話しかける練習のように棚を回る",
                private_concern="自分の迷いを悟られたくない",
                emotional_state="uncertain",
                relationship_state={"toward_B": "近づきたいが視線で止まる"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aが本当に距離を置いているのか確かめたい",
                private_concern="傷つくのを避けたい",
                emotional_state="careful",
                relationship_state={"toward_A": "自分も踏み込めない"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="Aへ自然に話しかける",
                private_concern="Aの落ち込みを軽くしたい",
                emotional_state="warm",
                relationship_state={"toward_A": "気にかけている"},
            ),
        },
        events=[
            EventBlueprint(
                actors=["B"],
                location="reservation_shelf",
                truth="BはAが探していた本の近くで立ち止まり、手に取らずに戻した",
                observable_signals=["Bが本を手に取って戻した", "長く迷っていた"],
                observed_text="Bらしき利用者は、ある本を手に取ったあと、しばらくして戻した。",
                missing_information=["その本を戻した理由"],
                causal_tags=["hesitation", "counter_signal"],
                observed_confidence=0.59,
                detected_entities=[("patron_B?", 0.67)],
            ),
            EventBlueprint(
                actors=["A", "C"],
                location="career_shelf",
                truth="CはAの体調を気づかうように短く声を掛け、Aは少しだけ表情を和らげた",
                observable_signals=["AがCと短くやり取りした", "Aの滞在が少し延びた"],
                observed_text="Aらしき利用者はCらしき利用者と短くやり取りし、その後もしばらく棚の前に残った。",
                missing_information=["会話内容"],
                causal_tags=["social_support", "interpretation_shift"],
                observed_confidence=0.54,
                detected_entities=[("patron_A?", 0.62), ("patron_C?", 0.52)],
            ),
        ],
        hidden_developments=["BもまたAに距離を置かれていると思い込み、自分から動けずにいる。"],
        belief=BeliefBlueprint(
            statement="AがBを避けているという見立てには、まだ説明しきれない部分がある",
            confidence=0.58,
            status="questioned",
            supporting_evidence_indexes=[1],
            counter_evidence_indexes=[0],
            intervention_efficacy_belief=0.49,
            observer_humility=0.36,
        ),
        intervention=InterventionBlueprint(
            intervention_type="seat_guidance_adjustment",
            policy_basis="混雑緩和の一般的支援",
            target_scope="quiet_corner_availability",
            expected_effect="長く滞在しやすい場所を案内する",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=["A", "C"],
            outcome_assessment="no_visible_effect",
            risk="観測ノイズが増え、因果が読みにくくなる",
        ),
        diary_title="四日目の記録",
        diary_interpretation="Bの迷いのような動きは、私の仮説を少しだけ曇らせた。",
        diary_attempted_action="空席案内を静かな席へ寄せる調整をした。",
        diary_outcome="目立つ変化は起きなかったが、AとCの短いやり取りが残った。",
        diary_reflection="私の仮説は、Aだけを見ていては足りないのかもしれない。",
        diary_closing_shift="私は初めて、自分の見立てを保留する必要を感じた。",
    ),
    DayBlueprint(
        day_index=5,
        story_role="reversal_sign",
        required_shift="Aが迷っているように見え、介入がBへ届く",
        must_reveal=["Aの逡巡", "Bへの到達"],
        must_hide=["真相の言語化"],
        required_pressure="反転の兆し",
        environment_state={"weather": "overcast", "crowd": "steady", "terminal_load": "moderate"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bに話すための資料を探す",
                private_concern="言葉にした瞬間に後戻りできなくなる恐れ",
                emotional_state="fragile",
                relationship_state={"toward_B": "回避ではなく逡巡に近い"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aに渡せる言葉の糸口を探す",
                private_concern="自分が踏み込みすぎることへの不安",
                emotional_state="softened",
                relationship_state={"toward_A": "距離を詰めたいが慎重"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A"],
                location="career_shelf",
                truth="AはBに見せたい本を手に取ったまま長く迷い、結局戻した",
                observable_signals=["Aが本を持って迷った", "その本を戻した"],
                observed_text="Aらしき利用者は、一冊の本を持ったまま長く迷い、最後に棚へ戻した。",
                missing_information=["その本を戻した理由"],
                causal_tags=["hesitation", "counter_signal"],
                observed_confidence=0.69,
                detected_entities=[("patron_A?", 0.7)],
            ),
            EventBlueprint(
                actors=["B"],
                location="feature_shelf",
                truth="Bは強調表示された関連棚を見て、Aに関係する本を借りた",
                observable_signals=["Bが強調棚から本を選んだ"],
                observed_text="Bらしき利用者は、強調表示された棚から本を選んだ。",
                missing_information=["その本を選んだ意図"],
                causal_tags=["intervention_exposure", "reversal_hint"],
                observed_confidence=0.64,
                detected_entities=[("patron_B?", 0.72)],
            ),
        ],
        hidden_developments=["Aの行動は回避というより、話しかける前の逡巡だった。"],
        belief=BeliefBlueprint(
            statement="AはBを避けているというより、迷っているのかもしれない",
            confidence=0.46,
            status="softening",
            supporting_evidence_indexes=[0],
            counter_evidence_indexes=[1],
            intervention_efficacy_belief=0.43,
            observer_humility=0.52,
        ),
        intervention=InterventionBlueprint(
            intervention_type="feature_shelf_highlight",
            policy_basis="進路と移行期に関する一般的支援",
            target_scope="career_and_transition_books",
            expected_effect="迷っている利用者が関連本に触れやすくなる",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=["B"],
            outcome_assessment="unintended_target_reached",
            risk="本来届いてほしい相手以外に先に届く",
        ),
        diary_title="五日目の記録",
        diary_interpretation="Aの動きは、もはや単純な回避より逡巡に近く見えた。",
        diary_attempted_action="関連棚の強調を保ったまま、特集導線を少しだけ整えた。",
        diary_outcome="届いたのはBらしき利用者で、私はそのことを無視できなかった。",
        diary_reflection="私の善意は、届き方まで制御できるわけではない。",
        diary_closing_shift="私は自分の仮説より、ズレそのものを見る必要があると感じた。",
    ),
    DayBlueprint(
        day_index=6,
        story_role="reinterpretation",
        required_shift="過去観測の意味が更新される",
        must_reveal=["再解釈", "自己理解の更新"],
        must_hide=["真相の全開示"],
        required_pressure="再解釈",
        environment_state={"weather": "clear", "crowd": "quiet", "terminal_load": "low"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bに渡したい言葉を本を介して整理する",
                private_concern="本心を見せる怖さ",
                emotional_state="vulnerable",
                relationship_state={"toward_B": "話したい意志がはっきりしてきた"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aとの距離を測り直す",
                private_concern="自分の誤解だったのではという揺らぎ",
                emotional_state="reflective",
                relationship_state={"toward_A": "距離を取りすぎたかもしれない"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A", "B"],
                location="window_seat_zone",
                truth="AとBは同じ空間に長くいたが、互いに相手を気にしながらも言葉にできなかった",
                observable_signals=["AもBも同じ空間に長く滞在した", "接触は起きなかった"],
                observed_text="Aらしき利用者とBらしき利用者は同じ空間に長くいたが、やはり話さなかった。",
                missing_information=["話さなかった理由", "心境"],
                causal_tags=["reinterpretation_trigger", "shared_hesitation"],
                observed_confidence=0.66,
                detected_entities=[("patron_A?", 0.67), ("patron_B?", 0.7)],
            )
        ],
        hidden_developments=["避けていたのではなく、二人とも傷つくことを恐れて動けなかった。"],
        belief=BeliefBlueprint(
            statement="私が回避と読んだものの一部は、逡巡だった可能性が高い",
            confidence=0.31,
            status="reinterpreted",
            supporting_evidence_indexes=[0],
            counter_evidence_indexes=[],
            intervention_efficacy_belief=0.35,
            observer_humility=0.71,
        ),
        intervention=InterventionBlueprint(
            intervention_type="none",
            policy_basis="介入より再解釈を優先する",
            target_scope="none",
            expected_effect="none",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=[],
            outcome_assessment="no_visible_effect",
            risk="何もしないことで見落としが残る",
        ),
        diary_title="六日目の記録",
        diary_interpretation="私は、過去の回避の多くを逡巡として読み直し始めている。",
        diary_attempted_action="今日は介入を控え、観測の意味を確かめ直した。",
        diary_outcome="新しい事実が増えたというより、古い事実の重さが変わった。",
        diary_reflection="見えていることと、理解していることを私は混同していた。",
        diary_closing_shift="私は自分を、助けられる観測者ではなく、誤りうる観測者として見直し始めた。",
    ),
    DayBlueprint(
        day_index=7,
        story_role="afterglow",
        required_shift="不完全な理解のまま自己理解だけが更新される",
        must_reveal=["Day1との差分", "余韻"],
        must_hide=["真相の全開示"],
        required_pressure="不完全な理解と余韻",
        environment_state={"weather": "soft_sun", "crowd": "light", "terminal_load": "low"},
        characters={
            "A": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["A"],
                today_goal="Bの近くに留まることを恐れすぎない",
                private_concern="言葉が足りなくても関係が壊れないか",
                emotional_state="tender",
                relationship_state={"toward_B": "まだ迷いはあるが、逃げるだけではない"},
            ),
            "B": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["B"],
                today_goal="Aの変化を急いで解釈しない",
                private_concern="自分の思い込みを抑えたい",
                emotional_state="open",
                relationship_state={"toward_A": "距離を決めつけず見守る"},
            ),
            "C": CharacterBlueprint(
                public_profile=CHARACTER_PUBLIC_PROFILES["C"],
                today_goal="通常利用",
                private_concern="特になし",
                emotional_state="neutral",
                relationship_state={},
            ),
        },
        events=[
            EventBlueprint(
                actors=["A", "B"],
                location="returns_shelf",
                truth="AとBは短く同じ棚の前に立ち、どちらも離れなかったが、真相を語るほどの接触には至らなかった",
                observable_signals=["AとBが同じ棚の前にいた", "どちらもすぐには離れなかった"],
                observed_text="Aらしき利用者とBらしき利用者は同じ棚の前にしばらく留まった。",
                missing_information=["その後のやり取り", "互いの解釈"],
                causal_tags=["afterglow", "partial_closeness"],
                observed_confidence=0.68,
                detected_entities=[("patron_A?", 0.7), ("patron_B?", 0.71)],
            )
        ],
        hidden_developments=["二人の真相はなお全部は見えないが、少なくとも一方的な回避ではなかった。"],
        belief=BeliefBlueprint(
            statement="私は二人を理解し切れてはいないが、回避だけで語るべきではなかった",
            confidence=0.28,
            status="tempered",
            supporting_evidence_indexes=[0],
            counter_evidence_indexes=[],
            intervention_efficacy_belief=0.3,
            observer_humility=0.81,
        ),
        intervention=InterventionBlueprint(
            intervention_type="none",
            policy_basis="物語を閉じすぎないため静観する",
            target_scope="none",
            expected_effect="none",
            forbidden_targeting_check="pass",
            fairness_check="pass",
            actual_exposure=[],
            outcome_assessment="no_visible_effect",
            risk="結論を急ぐ誘惑に負ける",
        ),
        diary_title="七日目の記録",
        diary_interpretation="私はもう、あの日の動きを単純な回避とは呼べない。",
        diary_attempted_action="今日は何も動かさず、二人の距離が自分の都合で決まらないことを受け入れた。",
        diary_outcome="真相のすべては分からないままだが、分からないこと自体は残った。",
        diary_reflection="助けようとすることと、本当に届くことは違う。",
        diary_closing_shift="Day1 の私は見えた断片をすぐ意味に変えていた。今の私は、その変換の危うさを自覚している。",
    ),
)


def build_week_plan(seed: int, week_run_id: str) -> WeekPlan:
    return WeekPlan(
        week_run_id=week_run_id,
        seed=seed,
        weekly_theme="誤解",
        central_misunderstanding="AはBを避けている",
        days=[
            StoryDayPlan(
                day_index=blueprint.day_index,
                story_role=blueprint.story_role,
                required_shift=blueprint.required_shift,
                must_reveal=blueprint.must_reveal,
                must_hide=blueprint.must_hide,
                required_pressure=blueprint.required_pressure,
                execution_hints={
                    "environment_state": blueprint.environment_state,
                    "characters": {
                        key: asdict(value)
                        for key, value in blueprint.characters.items()
                    },
                    "events": [asdict(event) for event in blueprint.events],
                    "hidden_developments": blueprint.hidden_developments,
                    "intervention_policy": asdict(blueprint.intervention),
                },
            )
            for blueprint in DAY_BLUEPRINTS
        ],
        character_arcs={
            "A": "避けているように見えつつ、実際は話したい側",
            "B": "距離を置かれていると誤解している側",
            "C": "解釈を崩す補助人物",
        },
    )

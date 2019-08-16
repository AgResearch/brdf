--
-- Name: gbs_sampleid_history_fact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbs_sampleid_history_fact
    ADD CONSTRAINT gbs_sampleid_history_fact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);



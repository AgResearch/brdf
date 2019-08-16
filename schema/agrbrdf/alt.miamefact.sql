--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY miamefact
    ADD CONSTRAINT "$1" FOREIGN KEY (microarraystudy) REFERENCES geneexpressionstudy(obid);



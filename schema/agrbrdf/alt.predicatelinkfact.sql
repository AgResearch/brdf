--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY predicatelinkfact
    ADD CONSTRAINT "$1" FOREIGN KEY (predicatelink) REFERENCES predicatelink(obid);



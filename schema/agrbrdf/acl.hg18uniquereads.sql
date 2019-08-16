--
-- Name: hg18uniquereads; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18uniquereads FROM PUBLIC;
REVOKE ALL ON TABLE hg18uniquereads FROM agrbrdf;
GRANT ALL ON TABLE hg18uniquereads TO agrbrdf;
GRANT SELECT ON TABLE hg18uniquereads TO gbs;


--
-- Name: samplesheet_factidseq; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON SEQUENCE samplesheet_factidseq FROM PUBLIC;
REVOKE ALL ON SEQUENCE samplesheet_factidseq FROM agrbrdf;
GRANT ALL ON SEQUENCE samplesheet_factidseq TO agrbrdf;
GRANT SELECT ON SEQUENCE samplesheet_factidseq TO gbs;


